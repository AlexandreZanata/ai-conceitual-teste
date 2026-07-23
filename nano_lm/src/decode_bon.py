"""Best-of-N with batched parallel sampling on GPU."""

from __future__ import annotations

import time
from typing import Any

import torch

from decode_ar import sample_next_batch
from scorers import DecodeResult, mean_logprob, pick_argmax


def decode_bon(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    n: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
    if n < 1:
        raise ValueError("n must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    base = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = base.shape[1]
    ids = base.repeat(n, 1)
    lps = torch.zeros(n, max_new_tokens, device=device)
    alive = torch.ones(n, dtype=torch.bool, device=device)
    token_evals = 0
    t0 = time.perf_counter()
    gen = 0
    for step in range(max_new_tokens):
        tok, lp, ev = sample_next_batch(
            model, ids, temperature=temperature, top_p=top_p
        )
        token_evals += ev
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
        gen = step + 1
        alive &= tok.squeeze(-1) != tokenizer.eos_token_id
        if not bool(alive.any()):
            break
    if device.type == "cuda":
        torch.cuda.synchronize()
    means = []
    for i in range(n):
        means.append(mean_logprob(lps[i, :gen].tolist()))
    best = pick_argmax(means)
    wall_ms = (time.perf_counter() - t0) * 1000.0
    new_ids = tuple(int(x) for x in ids[best, prompt_len:].tolist())
    text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
    return DecodeResult(
        token_ids=new_ids,
        text=text,
        mean_logprob=means[best],
        wall_ms=wall_ms,
        token_evals=token_evals,
    )
