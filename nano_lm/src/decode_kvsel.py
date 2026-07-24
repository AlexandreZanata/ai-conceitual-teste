"""EARLY decode with optional past_key_values (gated by caller)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from decode_early import _update_alive, decode_early
from scorers import DecodeResult, mean_logprob, pick_argmax


def decode_kvsel(
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
    use_kv: bool,
) -> DecodeResult:
    """
    GIVEN EARLY genes and use_kv flag
    WHEN decoding
    THEN KV path if use_kv else eager decode_early.
    """
    if not use_kv:
        return decode_early(
            model,
            tokenizer,
            prompt,
            n=n,
            max_new_tokens=max_new_tokens,
            min_new=min_new,
            conf_threshold=conf_threshold,
            patience=patience,
            temperature=temperature,
            top_p=top_p,
            seed=seed,
            device=device,
        )
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
    past = None
    t0 = time.perf_counter()
    gen = 0
    for step in range(max_new_tokens):
        with torch.no_grad():
            inp = ids if past is None else ids[:, -1:]
            out = model(inp, past_key_values=past, use_cache=True)
            past = out.past_key_values
            logits = out.logits[:, -1, :].float()
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
