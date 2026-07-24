"""Batched multi-prompt EARLY decode (shared forward per step)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from bat_ops import left_pad_batch
from decode_ar import top_p_filter
from early_ops import should_early_exit
from scorers import DecodeResult, mean_logprob, pick_argmax


def _update_alive(
    *,
    alive: torch.Tensor,
    tok: torch.Tensor,
    max_p: torch.Tensor,
    streaks: list[int],
    eos_id: int,
    gen: int,
    min_new: int,
    conf_threshold: float,
    patience: int,
) -> bool:
    stop_all = True
    for i in range(int(alive.shape[0])):
        if not bool(alive[i]):
            continue
        if int(tok[i].item()) == eos_id:
            alive[i] = False
            continue
        if float(max_p[i].item()) >= conf_threshold:
            streaks[i] += 1
        else:
            streaks[i] = 0
        if should_early_exit(
            n_new=gen, min_new=min_new, streak=streaks[i], patience=patience
        ):
            alive[i] = False
            continue
        stop_all = False
    return stop_all or not bool(alive.any())


def decode_early_batch(
    model: Any,
    tokenizer: Any,
    prompts: list[str],
    *,
    n: int,
    max_new_tokens: int,
    min_new: int,
    conf_threshold: float,
    patience: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
) -> tuple[list[DecodeResult], float]:
    """
    Decode many prompts in one rectangular batch (left-pad + attention_mask).
    Returns per-prompt best-of-n results and shared wall_ms.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if not prompts:
        raise ValueError("prompts must be non-empty")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    pad_id = int(tokenizer.pad_token_id)
    raw = [tokenizer.encode(p, add_special_tokens=False) for p in prompts]
    # Expand each prompt into n beams, then left-pad the full batch.
    expanded: list[list[int]] = []
    owners: list[int] = []
    for pi, seq in enumerate(raw):
        for _ in range(n):
            expanded.append(list(seq))
            owners.append(pi)
    padded, masks, prompt_lens = left_pad_batch(expanded, pad_id=pad_id)
    ids = torch.tensor(padded, dtype=torch.long, device=device)
    mask = torch.tensor(masks, dtype=torch.long, device=device)
    b = ids.shape[0]
    lps = torch.zeros(b, max_new_tokens, device=device)
    alive = torch.ones(b, dtype=torch.bool, device=device)
    streaks = [0] * b
    stop_at = [0] * b
    token_evals = 0
    t0 = time.perf_counter()
    gen = 0
    for step in range(max_new_tokens):
        with torch.no_grad():
            pos = mask.cumsum(dim=-1) - 1
            pos = pos.clamp(min=0)
            logits = model(
                ids, attention_mask=mask, position_ids=pos
            ).logits[:, -1, :].float()
            logits = logits / max(temperature, 1e-6)
            logits = top_p_filter(logits, top_p)
            probs = F.softmax(logits, dim=-1)
            max_p = probs.max(dim=-1).values
            if temperature < 1e-5:
                tok = probs.argmax(dim=-1, keepdim=True)
            else:
                tok = torch.multinomial(probs, num_samples=1)
            lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
        token_evals += int(b)
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
        mask = torch.cat([mask, torch.ones(b, 1, dtype=mask.dtype, device=device)], 1)
        gen = step + 1
        prev = alive.clone()
        done = _update_alive(
            alive=alive,
            tok=tok,
            max_p=max_p,
            streaks=streaks,
            eos_id=tokenizer.eos_token_id,
            gen=gen,
            min_new=min_new,
            conf_threshold=conf_threshold,
            patience=patience,
        )
        for i in range(b):
            if bool(prev[i]) and not bool(alive[i]) and stop_at[i] == 0:
                stop_at[i] = gen
        if done:
            break
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    for i in range(b):
        if stop_at[i] == 0:
            stop_at[i] = gen
    results: list[DecodeResult] = []
    for pi in range(len(prompts)):
        idxs = [i for i, o in enumerate(owners) if o == pi]
        means = [mean_logprob(lps[i, : stop_at[i]].tolist()) for i in idxs]
        best_local = pick_argmax(means)
        bi = idxs[best_local]
        plen = prompt_lens[bi]
        full = ids[bi].tolist()
        pad = ids.shape[1] - gen - plen
        end = pad + plen + stop_at[bi]
        new_ids = tuple(int(x) for x in full[pad + plen : end])
        text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
        results.append(
            DecodeResult(
                token_ids=new_ids,
                text=text,
                mean_logprob=means[best_local],
                wall_ms=wall_ms,
                token_evals=token_evals // max(len(prompts), 1),
            )
        )
    return results, wall_ms
