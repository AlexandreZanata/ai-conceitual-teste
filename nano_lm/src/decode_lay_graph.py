"""Batched EARLY+LAY decode with CUDA-graph full-depth forward (non-KV)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from bat_ops import left_pad_batch
from decode_ar import top_p_filter
from decode_bat import _update_alive
from decode_lay_batch import decode_lay_batch
from graph_ops import capture_one_seq_graph
from layer_exit import n_transformer_layers
from scorers import DecodeResult, mean_logprob, pick_argmax


def decode_lay_graph(
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
    max_skip: int,
    lay_conf: float,
    seed: int,
    device: torch.device,
) -> tuple[list[DecodeResult], float]:
    """
    GIVEN many prompts + EARLY knobs on CUDA
    WHEN left-pad batch and decode with lazy full-depth graphs
    THEN return per-prompt results; capture wall excluded from timed region.
    """
    if device.type != "cuda":
        return decode_lay_batch(
            model,
            tokenizer,
            prompts,
            n=n,
            max_new_tokens=max_new_tokens,
            min_new=min_new,
            conf_threshold=conf_threshold,
            patience=patience,
            temperature=temperature,
            top_p=top_p,
            max_skip=max_skip,
            lay_conf=lay_conf,
            seed=seed,
            device=device,
        )
    if n < 1:
        raise ValueError("n must be >= 1")
    if not prompts:
        raise ValueError("prompts must be non-empty")
    del max_skip, lay_conf  # full-depth graph path (parity with prior GRAPH)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    pad_id = int(tokenizer.pad_token_id)
    raw = [tokenizer.encode(p, add_special_tokens=False) for p in prompts]
    expanded: list[list[int]] = []
    owners: list[int] = []
    for pi, seq in enumerate(raw):
        for _ in range(n):
            expanded.append(list(seq))
            owners.append(pi)
    padded, masks, prompt_lens = left_pad_batch(expanded, pad_id=pad_id)
    ids = torch.tensor(padded, dtype=torch.long, device=device)
    mask = torch.tensor(masks, dtype=torch.long, device=device)
    b = int(ids.shape[0])
    vocab = int(model.config.vocab_size)
    n_layers = n_transformer_layers(model)
    graphs: dict[int, tuple[Any, Any, Any, Any, Any]] = {}
    lps = torch.zeros(b, max_new_tokens, device=device)
    alive = torch.ones(b, dtype=torch.bool, device=device)
    streaks = [0] * b
    stop_at = [0] * b
    token_evals = 0
    layer_evals = 0
    wall_ms = 0.0
    gen = 0
    prev_t: int | None = None
    for step in range(max_new_tokens):
        pos = (mask.cumsum(dim=-1) - 1).clamp(min=0)
        t = int(ids.shape[1])
        if t not in graphs:
            # Capture untimed; keep ≤1 prior graph to bound VRAM.
            graphs[t] = capture_one_seq_graph(
                model, batch=b, t=t, device=device, vocab=vocab
            )
            if prev_t is not None and prev_t in graphs and prev_t != t:
                del graphs[prev_t]
                torch.cuda.empty_cache()
        prev_t = t
        graph, s_ids, s_mask, s_pos, s_out = graphs[t]
        torch.cuda.synchronize()
        t_step = time.perf_counter()
        s_ids.copy_(ids)
        s_mask.copy_(mask)
        s_pos.copy_(pos)
        graph.replay()
        logits = s_out.float() / max(temperature, 1e-6)
        logits = top_p_filter(logits, top_p)
        probs = F.softmax(logits, dim=-1)
        max_p = probs.max(dim=-1).values
        if temperature < 1e-5:
            tok = probs.argmax(dim=-1, keepdim=True)
        else:
            tok = torch.multinomial(probs, num_samples=1)
        lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
        token_evals += int(b)
        layer_evals += int(n_layers) * int(b)
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
        torch.cuda.synchronize()
        wall_ms += (time.perf_counter() - t_step) * 1000.0
        if done:
            break
    del graphs
    torch.cuda.empty_cache()
    for i in range(b):
        if stop_at[i] == 0:
            stop_at[i] = gen
    results: list[DecodeResult] = []
    n_prompts = max(len(prompts), 1)
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
                token_evals=token_evals // n_prompts,
                layer_evals=layer_evals // n_prompts,
            )
        )
    return results, wall_ms
