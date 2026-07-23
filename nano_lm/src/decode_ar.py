"""Autoregressive sampling — single and batched (GPU-friendly)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from scorers import DecodeResult, mean_logprob


def _top_p_filter(logits: torch.Tensor, top_p: float) -> torch.Tensor:
    sorted_logits, sorted_idx = torch.sort(logits, descending=True)
    probs = F.softmax(sorted_logits, dim=-1)
    cum = torch.cumsum(probs, dim=-1)
    mask = cum > top_p
    mask[..., 1:] = mask[..., :-1].clone()
    mask[..., 0] = False
    sorted_logits = sorted_logits.masked_fill(mask, float("-inf"))
    return torch.zeros_like(logits).scatter(-1, sorted_idx, sorted_logits)


def sample_next_batch(
    model: Any,
    input_ids: torch.Tensor,
    *,
    temperature: float,
    top_p: float,
) -> tuple[torch.Tensor, torch.Tensor, int]:
    """Batched next-token sample. Returns tokens [B,1], logprobs [B], evals=B."""
    with torch.no_grad():
        logits = model(input_ids).logits[:, -1, :].float()
        logits = logits / max(temperature, 1e-6)
        logits = _top_p_filter(logits, top_p)
        probs = F.softmax(logits, dim=-1)
        token = torch.multinomial(probs, num_samples=1)
        logp = torch.log(probs.gather(-1, token).squeeze(-1) + 1e-12)
    return token, logp, int(input_ids.shape[0])


def sample_next(
    model: Any,
    input_ids: torch.Tensor,
    *,
    temperature: float,
    top_p: float,
) -> tuple[int, float, int]:
    tok, logp, ev = sample_next_batch(
        model, input_ids, temperature=temperature, top_p=top_p
    )
    return int(tok.item()), float(logp.item()), ev


def decode_ar(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = ids.shape[1]
    logprobs: list[float] = []
    token_evals = 0
    t0 = time.perf_counter()
    for _ in range(max_new_tokens):
        tok_t, lp_t, ev = sample_next_batch(
            model, ids, temperature=temperature, top_p=top_p
        )
        token_evals += ev
        logprobs.append(float(lp_t.item()))
        ids = torch.cat([ids, tok_t], dim=1)
        if int(tok_t.item()) == tokenizer.eos_token_id:
            break
    wall_ms = (time.perf_counter() - t0) * 1000.0
    new_ids = tuple(int(x) for x in ids[0, prompt_len:].tolist())
    text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
    return DecodeResult(
        token_ids=new_ids,
        text=text,
        mean_logprob=mean_logprob(logprobs),
        wall_ms=wall_ms,
        token_evals=token_evals,
    )
