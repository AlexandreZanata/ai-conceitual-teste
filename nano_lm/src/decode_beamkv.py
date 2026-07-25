"""PFB multi-beam decode: shared prompt KV vs independent prefills."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F
from transformers.cache_utils import DynamicCache

from decode_ar import top_p_filter
from decode_early import _update_alive
from scorers import DecodeResult, mean_logprob

__all__ = [
    "expand_past_to_batch",
    "decode_beams_shared_kv",
    "decode_beams_indep_kv",
]


def expand_past_to_batch(past: Any, n: int) -> Any:
    """Expand bsz=1 past_key_values to batch n (mutates DynamicCache)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    if n == 1:
        return past
    cache = past
    if not isinstance(cache, DynamicCache):
        cache = DynamicCache.from_legacy_cache(cache)
    cache.batch_repeat_interleave(n)
    return cache


def decode_beams_shared_kv(
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
) -> list[DecodeResult]:
    """Prefill prompt once, expand KV to n beams, generate (shared wall)."""
    if n < 1:
        raise ValueError("n must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    base = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = int(base.shape[1])
    t0 = time.perf_counter()
    with torch.no_grad():
        out = model(base, use_cache=True)
        logits = out.logits[:, -1, :].float().repeat(n, 1)
        past = expand_past_to_batch(out.past_key_values, n)
    token_evals = 1
    ids = base.repeat(n, 1)
    lps = torch.zeros(n, max_new_tokens, device=device)
    alive = torch.ones(n, dtype=torch.bool, device=device)
    streaks = [0] * n
    gen = 0
    for step in range(max_new_tokens):
        tok, max_p, lp = _sample_row(logits, temperature=temperature, top_p=top_p)
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
        token_evals += n
    return _pack_results(
        tokenizer, ids, lps, gen, prompt_len, n, t0, device, token_evals
    )


def decode_beams_indep_kv(
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
) -> list[DecodeResult]:
    """Each beam prefills independently; one wall covers all K prefills."""
    if n < 1:
        raise ValueError("n must be >= 1")
    t0 = time.perf_counter()
    parts: list[DecodeResult] = []
    token_evals = 0
    for i in range(n):
        one = decode_beams_shared_kv(
            model,
            tokenizer,
            prompt,
            n=1,
            max_new_tokens=max_new_tokens,
            min_new=min_new,
            conf_threshold=conf_threshold,
            patience=patience,
            temperature=temperature,
            top_p=top_p,
            seed=seed + i,
            device=device,
        )[0]
        token_evals += int(one.token_evals)
        parts.append(one)
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    return [
        DecodeResult(
            token_ids=r.token_ids,
            text=r.text,
            mean_logprob=r.mean_logprob,
            wall_ms=wall_ms,
            token_evals=token_evals,
        )
        for r in parts
    ]


def _sample_row(
    logits: torch.Tensor, *, temperature: float, top_p: float
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
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


def _pack_results(
    tokenizer: Any,
    ids: torch.Tensor,
    lps: torch.Tensor,
    gen: int,
    prompt_len: int,
    n: int,
    t0: float,
    device: torch.device,
    token_evals: int,
) -> list[DecodeResult]:
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    out: list[DecodeResult] = []
    for i in range(n):
        new_ids = tuple(int(x) for x in ids[i, prompt_len:].tolist())
        text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
        out.append(
            DecodeResult(
                token_ids=new_ids,
                text=text,
                mean_logprob=mean_logprob(lps[i, :gen].tolist()),
                wall_ms=wall_ms,
                token_evals=token_evals,
            )
        )
    return out
