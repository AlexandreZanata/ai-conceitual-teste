"""Beam search decode (student); multi-path vs BoN sampling."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from scorers import DecodeResult, mean_logprob


def _beam_score(log_sum: float, length: int, length_penalty: float) -> float:
    if length < 1:
        return float("-inf")
    return float(log_sum) / (float(length) ** max(0.0, float(length_penalty)))


def decode_beam(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    beam_width: int,
    max_new_tokens: int,
    length_penalty: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
    if beam_width < 1:
        raise ValueError("beam_width must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    base = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = int(base.shape[1])
    # beams: (ids [1,T], sum_logprob, finished)
    beams: list[tuple[torch.Tensor, float, bool]] = [(base, 0.0, False)]
    token_evals = 0
    t0 = time.perf_counter()
    for _ in range(max_new_tokens):
        if all(b[2] for b in beams):
            break
        cands: list[tuple[torch.Tensor, float, bool]] = []
        for ids, log_sum, done in beams:
            if done:
                cands.append((ids, log_sum, True))
                continue
            with torch.no_grad():
                logits = model(ids).logits[:, -1, :].float()
                logp = F.log_softmax(logits, dim=-1)[0]
            token_evals += 1
            topv, topi = torch.topk(logp, k=min(beam_width, logp.numel()))
            for v, i in zip(topv.tolist(), topi.tolist()):
                tok = int(i)
                new_ids = torch.cat(
                    [ids, torch.tensor([[tok]], device=device, dtype=ids.dtype)],
                    dim=1,
                )
                finished = tok == tokenizer.eos_token_id
                cands.append((new_ids, log_sum + float(v), finished))
        cands.sort(
            key=lambda c: _beam_score(
                c[1], int(c[0].shape[1]) - prompt_len, length_penalty
            ),
            reverse=True,
        )
        beams = cands[:beam_width]
    if device.type == "cuda":
        torch.cuda.synchronize()
    best_ids, best_sum, _ = max(
        beams,
        key=lambda b: _beam_score(
            b[1], max(1, int(b[0].shape[1]) - prompt_len), length_penalty
        ),
    )
    wall_ms = (time.perf_counter() - t0) * 1000.0
    new_ids = tuple(int(x) for x in best_ids[0, prompt_len:].tolist())
    n = max(1, len(new_ids))
    text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
    return DecodeResult(
        token_ids=new_ids,
        text=text,
        mean_logprob=mean_logprob([best_sum / n] * n) if new_ids else float("-inf"),
        wall_ms=wall_ms,
        token_evals=token_evals,
    )
