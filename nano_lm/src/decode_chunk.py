"""EARLY decode with chunked KV prefill (block size B)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from decode_early import _update_alive
from scorers import DecodeResult, mean_logprob, pick_argmax


def decode_early_chunked(
    model: Any,
    tokenizer: Any,
    prompt: str,
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
    chunk_size: int,
) -> DecodeResult:
    """
    GIVEN EARLY genes and chunk_size B
    WHEN prefilling prompt in blocks of B with KV, then generating
    THEN return DecodeResult (same contract as decode_early).
    """
    if n < 1:
        raise ValueError("n must be >= 1")
    if int(chunk_size) < 1:
        raise ValueError("chunk_size must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    base = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = int(base.shape[1])
    ids = base.repeat(n, 1)
    b = int(chunk_size)
    t0 = time.perf_counter()
    logits, past = _prefill(model, ids, prompt_len=prompt_len, chunk_size=b)
    ids, lps, gen, token_evals = _generate(
        model,
        tokenizer,
        ids=ids,
        logits=logits,
        past=past,
        n=n,
        max_new_tokens=max_new_tokens,
        min_new=min_new,
        conf_threshold=conf_threshold,
        patience=patience,
        temperature=temperature,
        top_p=top_p,
        token_evals=n * ((prompt_len + b - 1) // b),
    )
    if device.type == "cuda":
        torch.cuda.synchronize()
    means = [mean_logprob(lps[i, :gen].tolist()) for i in range(n)]
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


def _prefill(
    model: Any,
    ids: torch.Tensor,
    *,
    prompt_len: int,
    chunk_size: int,
) -> tuple[torch.Tensor, Any]:
    """Return (logits at prompt end, past_key_values)."""
    past = None
    logits: torch.Tensor | None = None
    pos = 0
    with torch.no_grad():
        while pos < prompt_len:
            end = min(pos + chunk_size, prompt_len)
            out = model(ids[:, pos:end], past_key_values=past, use_cache=True)
            past = out.past_key_values
            logits = out.logits[:, -1, :].float()
            pos = end
    assert logits is not None
    return logits, past


def _generate(
    model: Any,
    tokenizer: Any,
    *,
    ids: torch.Tensor,
    logits: torch.Tensor,
    past: Any,
    n: int,
    max_new_tokens: int,
    min_new: int,
    conf_threshold: float,
    patience: int,
    temperature: float,
    top_p: float,
    token_evals: int,
) -> tuple[torch.Tensor, torch.Tensor, int, int]:
    """Sample until early-exit; return (ids, lps, gen, token_evals)."""
    lps = torch.zeros(n, max_new_tokens, device=ids.device)
    alive = torch.ones(n, dtype=torch.bool, device=ids.device)
    streaks = [0] * n
    gen = 0
    for step in range(max_new_tokens):
        tok, max_p, lp = _sample(logits, temperature=temperature, top_p=top_p)
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
        gen = step + 1
        if _update_alive(
            alive=alive,
            tok=tok,
            max_p=max_p,
            streaks=streaks,
            eos_id=tokenizer.eos_token_id,
            gen=gen,
            min_new=min_new,
            conf_threshold=conf_threshold,
            patience=patience,
        ):
            break
        with torch.no_grad():
            out = model(tok, past_key_values=past, use_cache=True)
            past = out.past_key_values
            logits = out.logits[:, -1, :].float()
        token_evals += int(n)
    return ids, lps, gen, token_evals


def _sample(
    logits: torch.Tensor, *, temperature: float, top_p: float
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
    """Return (tok, max_p, lp) from last-step logits."""
    logits = logits / max(temperature, 1e-6)
    logits = top_p_filter(logits, top_p)
    probs = F.softmax(logits, dim=-1)
    max_p = probs.max(dim=-1).values
    if temperature < 1e-5:
        tok = probs.argmax(dim=-1, keepdim=True)
    else:
        tok = torch.multinomial(probs, num_samples=1)
    lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
    return tok, max_p, lp
