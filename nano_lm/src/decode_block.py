"""Block-parallel decode: sample a block from one forward (no mid-block AR)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from scorers import DecodeResult, mean_logprob


def decode_block(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    max_new_tokens: int,
    block_size: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
    """
    GIVEN a causal LM and block_size ≥ 1
    WHEN decoding
    THEN each forward yields up to block_size independent samples from p(·|prefix),
         appended without reconditioning inside the block.
    """
    if block_size < 1:
        raise ValueError("decode_block: block_size must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = ids.shape[1]
    logprobs: list[float] = []
    token_evals = 0
    t0 = time.perf_counter()
    made = 0
    while made < max_new_tokens:
        with torch.no_grad():
            logits = model(ids).logits[:, -1, :].float()
            logits = logits / max(temperature, 1e-6)
            logits = top_p_filter(logits, top_p)
            probs = F.softmax(logits, dim=-1)
        token_evals += int(ids.shape[0])
        take = min(int(block_size), max_new_tokens - made)
        for _ in range(take):
            tok = torch.multinomial(probs, num_samples=1)
            lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
            logprobs.append(float(lp.item()))
            ids = torch.cat([ids, tok], dim=1)
            made += 1
            if int(tok.item()) == tokenizer.eos_token_id:
                made = max_new_tokens
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
