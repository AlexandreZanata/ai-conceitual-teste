"""Lookahead MAE with batched K candidates (loads the GPU)."""

from __future__ import annotations

import time
from typing import Any

import torch

from decode_ar import sample_next_batch
from scorers import DecodeResult, mean_logprob, pick_argmax


def _advance_batch(
    model: Any,
    ids: torch.Tensor,
    steps: int,
    *,
    temperature: float,
    top_p: float,
) -> tuple[torch.Tensor, torch.Tensor, int]:
    """Run `steps` batched samples. Returns ids, logprobs [B,steps], evals."""
    b = ids.shape[0]
    lps = torch.empty(b, steps, device=ids.device, dtype=torch.float32)
    evals = 0
    cur = ids
    for s in range(steps):
        tok, lp, ev = sample_next_batch(
            model, cur, temperature=temperature, top_p=top_p
        )
        evals += ev
        lps[:, s] = lp
        cur = torch.cat([cur, tok], dim=1)
    return cur, lps, evals


def decode_mae(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    k: int,
    block: int,
    horizon: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
    if k < 1 or block < 1 or horizon < 1:
        raise ValueError("k, block, horizon must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    base = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = base.shape[1]
    ids = base
    all_lps: list[float] = []
    token_evals = 0
    t0 = time.perf_counter()
    generated = 0
    while generated < max_new_tokens:
        step = min(block, max_new_tokens - generated)
        batch = ids.repeat(k, 1)
        batch, block_lps, ev = _advance_batch(
            model, batch, step, temperature=temperature, top_p=top_p
        )
        token_evals += ev
        scored, hor_lps, hev = _advance_batch(
            model, batch, horizon, temperature=temperature, top_p=top_p
        )
        token_evals += hev
        scores = hor_lps.mean(dim=1).tolist()
        best = pick_argmax(scores)
        ids = batch[best : best + 1, :]
        all_lps.extend(float(x) for x in block_lps[best].tolist())
        generated += step
        del scored
        if tokenizer.eos_token_id in ids[0, prompt_len:].tolist():
            break
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    new_ids = tuple(int(x) for x in ids[0, prompt_len:].tolist())
    text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
    return DecodeResult(
        token_ids=new_ids,
        text=text,
        mean_logprob=mean_logprob(all_lps),
        wall_ms=wall_ms,
        token_evals=token_evals,
    )
