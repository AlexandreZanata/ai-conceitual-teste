"""Batched BoN decode with chunked KV prefill (block size B)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from bat_ops import left_pad_batch
from cbat_steps import prefill_chunked
from decode_ar import top_p_filter
from scorers import DecodeResult, mean_logprob, pick_argmax


def decode_bon_batch_chunked(
    model: Any,
    tokenizer: Any,
    prompts: list[str],
    *,
    n: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
    chunk_size: int,
) -> tuple[list[DecodeResult], float]:
    """
    GIVEN many prompts, BoN width n, chunk_size B
    WHEN left-pad batch, prefill in blocks of B with KV, then generate to EOS
    THEN return per-prompt best-of-n results and shared wall_ms.
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if int(chunk_size) < 1:
        raise ValueError("chunk_size must be >= 1")
    if not prompts:
        raise ValueError("prompts must be non-empty")
    torch.manual_seed(seed)
    if device.type == "cuda":
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
    bsz = ids.shape[0]
    prompt_len = int(ids.shape[1])
    t0 = time.perf_counter()
    logits, past, token_evals = prefill_chunked(
        model, ids, mask, chunk_size=int(chunk_size)
    )
    ids, mask, lps, gen, stop_at, token_evals = _generate_bon(
        model,
        tokenizer,
        ids=ids,
        mask=mask,
        logits=logits,
        past=past,
        bsz=bsz,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        top_p=top_p,
        token_evals=token_evals,
    )
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    results = _pack(
        tokenizer,
        prompts,
        owners,
        ids,
        lps,
        prompt_lens,
        stop_at,
        gen,
        wall_ms,
        token_evals,
        prompt_len=prompt_len,
    )
    return results, wall_ms


def _generate_bon(
    model: Any,
    tokenizer: Any,
    *,
    ids: torch.Tensor,
    mask: torch.Tensor,
    logits: torch.Tensor,
    past: Any,
    bsz: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    token_evals: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, int, list[int], int]:
    lps = torch.zeros(bsz, max_new_tokens, device=ids.device)
    alive = torch.ones(bsz, dtype=torch.bool, device=ids.device)
    stop_at = [0] * bsz
    gen = 0
    for step in range(max_new_tokens):
        tok, lp = _sample(logits, temperature=temperature, top_p=top_p)
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
        ones = torch.ones(bsz, 1, dtype=mask.dtype, device=mask.device)
        mask = torch.cat([mask, ones], 1)
        gen = step + 1
        prev = alive.clone()
        alive &= tok.squeeze(-1) != tokenizer.eos_token_id
        for i in range(bsz):
            if bool(prev[i]) and not bool(alive[i]) and stop_at[i] == 0:
                stop_at[i] = gen
        if not bool(alive.any()):
            break
        with torch.no_grad():
            pids = (mask.cumsum(dim=-1) - 1).clamp(min=0)[:, -1:]
            out = model(
                tok,
                attention_mask=mask,
                position_ids=pids,
                past_key_values=past,
                use_cache=True,
            )
            past = out.past_key_values
            logits = out.logits[:, -1, :].float()
        token_evals += bsz
    for i in range(bsz):
        if stop_at[i] == 0:
            stop_at[i] = gen
    return ids, mask, lps, gen, stop_at, token_evals


def _sample(
    logits: torch.Tensor, *, temperature: float, top_p: float
) -> tuple[torch.Tensor, torch.Tensor]:
    logits = logits / max(temperature, 1e-6)
    logits = top_p_filter(logits, top_p)
    probs = F.softmax(logits, dim=-1)
    if temperature < 1e-5:
        tok = probs.argmax(dim=-1, keepdim=True)
    else:
        tok = torch.multinomial(probs, num_samples=1)
    lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
    return tok, lp


def _pack(
    tokenizer: Any,
    prompts: list[str],
    owners: list[int],
    ids: torch.Tensor,
    lps: torch.Tensor,
    prompt_lens: list[int],
    stop_at: list[int],
    gen: int,
    wall_ms: float,
    token_evals: int,
    *,
    prompt_len: int,
) -> list[DecodeResult]:
    out: list[DecodeResult] = []
    for pi in range(len(prompts)):
        idxs = [i for i, o in enumerate(owners) if o == pi]
        means = [mean_logprob(lps[i, : stop_at[i]].tolist()) for i in idxs]
        best_local = pick_argmax(means)
        bi = idxs[best_local]
        plen = prompt_lens[bi]
        full = ids[bi].tolist()
        pad = prompt_len - plen
        end = pad + plen + stop_at[bi]
        new_ids = tuple(int(x) for x in full[pad + plen : end])
        text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
        out.append(
            DecodeResult(
                token_ids=new_ids,
                text=text,
                mean_logprob=means[best_local],
                wall_ms=wall_ms,
                token_evals=token_evals // max(len(prompts), 1),
            )
        )
    return out
