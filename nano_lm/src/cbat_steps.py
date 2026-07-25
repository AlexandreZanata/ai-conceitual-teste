"""Prefill + generate steps for batched chunked EARLY decode."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from decode_bat import _update_alive

__all__ = ["prefill_chunked", "generate_chunked"]


def prefill_chunked(
    model: Any,
    ids: torch.Tensor,
    mask: torch.Tensor,
    *,
    chunk_size: int,
) -> tuple[torch.Tensor, Any, int]:
    """Return (logits at prompt end, past_key_values, token_evals)."""
    past = None
    logits: torch.Tensor | None = None
    pos = 0
    prompt_len = int(ids.shape[1])
    token_evals = 0
    bsz = int(ids.shape[0])
    with torch.no_grad():
        while pos < prompt_len:
            end = min(pos + chunk_size, prompt_len)
            chunk = ids[:, pos:end]
            am = mask[:, :end]
            pids = (am.cumsum(dim=-1) - 1).clamp(min=0)[:, pos:end]
            out = model(
                chunk,
                attention_mask=am,
                position_ids=pids,
                past_key_values=past,
                use_cache=True,
            )
            past = out.past_key_values
            logits = out.logits[:, -1, :].float()
            token_evals += bsz
            pos = end
    assert logits is not None
    return logits, past, token_evals


def generate_chunked(
    model: Any,
    tokenizer: Any,
    *,
    ids: torch.Tensor,
    mask: torch.Tensor,
    logits: torch.Tensor,
    past: Any,
    bsz: int,
    max_new_tokens: int,
    min_new: int,
    conf_threshold: float,
    patience: int,
    temperature: float,
    top_p: float,
    token_evals: int,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, int, list[int], int]:
    """Sample until early-exit; return ids, mask, lps, gen, stop_at, token_evals."""
    lps = torch.zeros(bsz, max_new_tokens, device=ids.device)
    alive = torch.ones(bsz, dtype=torch.bool, device=ids.device)
    streaks = [0] * bsz
    stop_at = [0] * bsz
    gen = 0
    for step in range(max_new_tokens):
        tok, max_p, lp = _sample(logits, temperature=temperature, top_p=top_p)
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
        ones = torch.ones(bsz, 1, dtype=mask.dtype, device=mask.device)
        mask = torch.cat([mask, ones], 1)
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
        for i in range(bsz):
            if bool(prev[i]) and not bool(alive[i]) and stop_at[i] == 0:
                stop_at[i] = gen
        if done:
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
