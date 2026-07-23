"""Iterative discrete diffusion decode (remask → predict → fill)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from scorers import DecodeResult, mean_logprob


def decode_dif(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    max_new_tokens: int,
    dif_steps: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
    mask_id: int | None = None,
) -> DecodeResult:
    """
    GIVEN a diffusion-trained LM
    WHEN sampling a continuation
    THEN run dif_steps remask/predict passes over a max_new block (slow path).
    """
    if dif_steps < 1:
        raise ValueError("decode_dif: dif_steps must be >= 1")
    if max_new_tokens < 1:
        raise ValueError("decode_dif: max_new_tokens must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    mid = int(mask_id if mask_id is not None else tokenizer.eos_token_id)
    prompt_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = int(prompt_ids.shape[1])
    cont = torch.full(
        (1, max_new_tokens), mid, dtype=prompt_ids.dtype, device=device
    )
    token_evals = 0
    last_lps: list[float] = []
    t0 = time.perf_counter()
    for step in range(int(dif_steps)):
        rate = 1.0 - float(step + 1) / float(dif_steps)
        if rate > 0.0:
            noise = torch.rand(cont.shape, device=device) < rate
            cont = cont.clone()
            cont[noise] = mid
        ids = torch.cat([prompt_ids, cont], dim=1)
        with torch.no_grad():
            logits = model(ids).logits[:, prompt_len - 1 : -1, :].float()
            logits = logits / max(temperature, 1e-6)
            logits = top_p_filter(logits, top_p)
            probs = F.softmax(logits, dim=-1)
            flat = probs.reshape(-1, probs.shape[-1])
            tok = torch.multinomial(flat, num_samples=1)
            lp = torch.log(flat.gather(-1, tok).squeeze(-1) + 1e-12)
        token_evals += int(ids.shape[0])
        cont = tok.reshape(1, max_new_tokens)
        last_lps = [float(x) for x in lp.tolist()]
        if device.type == "cuda":
            torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    new_ids = tuple(int(x) for x in cont[0].tolist())
    text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
    return DecodeResult(
        token_ids=new_ids,
        text=text,
        mean_logprob=mean_logprob(last_lps) if last_lps else float("-inf"),
        wall_ms=wall_ms,
        token_evals=token_evals,
    )
