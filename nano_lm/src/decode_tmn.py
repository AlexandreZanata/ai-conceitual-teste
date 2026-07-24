"""AR decode with typical + min-p filters (TYP × MINP)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from minp_ops import apply_min_p
from scorers import DecodeResult, mean_logprob
from typ_ops import apply_typical


def decode_tmn(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    typ_mass: float,
    min_p: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
    """
    GIVEN typ_mass in (0,1] and min_p in [0,1)
    WHEN sampling
    THEN apply typical, then min-p, then top-p.
    """
    if not (0.0 < float(typ_mass) <= 1.0):
        raise ValueError("decode_tmn: typ_mass must be in (0,1]")
    if not (0.0 <= float(min_p) < 1.0):
        raise ValueError("decode_tmn: min_p must be in [0,1)")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = ids.shape[1]
    logprobs: list[float] = []
    token_evals = 0
    t0 = time.perf_counter()
    for _ in range(max_new_tokens):
        with torch.no_grad():
            logits = model(ids).logits[:, -1, :].float()
            logits = logits / max(temperature, 1e-6)
            logits = apply_typical(logits, typ_mass)
            logits = apply_min_p(logits, min_p)
            logits = top_p_filter(logits, top_p)
            probs = F.softmax(logits, dim=-1)
            tok = torch.multinomial(probs, num_samples=1)
            lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
        token_evals += int(ids.shape[0])
        logprobs.append(float(lp.item()))
        ids = torch.cat([ids, tok], dim=1)
        if int(tok.item()) == tokenizer.eos_token_id:
            break
        if device.type == "cuda":
            torch.cuda.synchronize()
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
