"""EARLY multi-beam decode returning all candidates (H-ABS-PFB)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from decode_early import _update_alive
from scorers import DecodeResult, mean_logprob


def decode_early_beams(
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
    """
    GIVEN EARLY knobs and n≥1 beams
    WHEN decoding without student-lp commit
    THEN return one DecodeResult per beam (wall shared).
    """
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
    streaks = [0] * n
    token_evals = 0
    t0 = time.perf_counter()
    gen = 0
    for step in range(max_new_tokens):
        with torch.no_grad():
            logits = model(ids).logits[:, -1, :].float()
            logits = logits / max(temperature, 1e-6)
            logits = top_p_filter(logits, top_p)
            probs = F.softmax(logits, dim=-1)
            max_p = probs.max(dim=-1).values
            if temperature < 1e-5:
                tok = probs.argmax(dim=-1, keepdim=True)
            else:
                tok = torch.multinomial(probs, num_samples=1)
            lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
        token_evals += int(ids.shape[0])
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
