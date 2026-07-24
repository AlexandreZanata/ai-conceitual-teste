"""BoN early-exit with gene max_new + conf metrics (H-EAR2)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from ear2_ops import conf_score
from early_ops import should_early_exit
from scorers import DecodeResult, mean_logprob, pick_argmax


def _update_alive(
    *,
    alive: torch.Tensor,
    tok: torch.Tensor,
    score: torch.Tensor,
    streaks: list[int],
    eos_id: int,
    gen: int,
    min_new: int,
    conf_threshold: float,
    patience: int,
) -> bool:
    stop_all = True
    for i in range(int(alive.shape[0])):
        if not bool(alive[i]):
            continue
        if int(tok[i].item()) == eos_id:
            alive[i] = False
            continue
        if float(score[i].item()) >= conf_threshold:
            streaks[i] += 1
        else:
            streaks[i] = 0
        if should_early_exit(
            n_new=gen, min_new=min_new, streak=streaks[i], patience=patience
        ):
            alive[i] = False
            continue
        stop_all = False
    return stop_all or not bool(alive.any())


def decode_ear2(
    model: Any,
    tokenizer: Any,
    prompt: str,
    *,
    n: int,
    max_new_tokens: int,
    min_new: int,
    conf_threshold: float,
    patience: int,
    conf_metric: str,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
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
            score = conf_score(probs, conf_metric)
            tok = torch.multinomial(probs, num_samples=1)
            lp = torch.log(probs.gather(-1, tok).squeeze(-1) + 1e-12)
        token_evals += int(ids.shape[0])
        lps[:, step] = lp
        ids = torch.cat([ids, tok], dim=1)
        gen = step + 1
        if _update_alive(
            alive=alive,
            tok=tok,
            score=score,
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
