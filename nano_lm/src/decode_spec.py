"""Speculative decode: student drafts, teacher verifies (Leviathan-style)."""

from __future__ import annotations

import time
from typing import Any

import torch
import torch.nn.functional as F

from decode_ar import top_p_filter
from scorers import DecodeResult, mean_logprob
from spec_accept import accept_prefix_len


def _draft_block(
    student: Any,
    ids: torch.Tensor,
    draft_len: int,
    *,
    temperature: float,
    top_p: float,
) -> tuple[torch.Tensor, list[torch.Tensor], list[int], int]:
    """Sample draft tokens; return ids, q-dists, token ids, evals."""
    q_dists: list[torch.Tensor] = []
    toks: list[int] = []
    evals = 0
    cur = ids
    for _ in range(draft_len):
        with torch.no_grad():
            logits = student(cur).logits[:, -1, :].float()
            logits = logits / max(temperature, 1e-6)
            logits = top_p_filter(logits, top_p)
            probs = F.softmax(logits, dim=-1)
            tok = torch.multinomial(probs, num_samples=1)
        evals += 1
        q_dists.append(probs[0].detach())
        toks.append(int(tok.item()))
        cur = torch.cat([cur, tok], dim=1)
    return cur, q_dists, toks, evals


def _sample_residual(p_vocab: torch.Tensor, q_vocab: torch.Tensor) -> int:
    raw = torch.clamp(p_vocab - q_vocab, min=0.0)
    mass = float(raw.sum().item())
    if mass <= 1e-12:
        flat = torch.ones_like(p_vocab) / p_vocab.numel()
        return int(torch.multinomial(flat, 1).item())
    return int(torch.multinomial(raw / mass, 1).item())


def _verify(
    teacher: Any,
    drafted: torch.Tensor,
    q_dists: list[torch.Tensor],
    toks: list[int],
) -> tuple[list[int], int]:
    """Accept draft prefix; residual sample on reject; else +1 from teacher."""
    n = len(toks)
    with torch.no_grad():
        all_logits = teacher(drafted).logits.float()
        step = all_logits[:, -(n + 1) : -1, :]
        p_dists = [F.softmax(step[0, i], dim=-1) for i in range(n)]
        bonus = F.softmax(all_logits[:, -1, :], dim=-1)
    d_probs = [float(q_dists[i][toks[i]].item()) for i in range(n)]
    t_probs = [float(p_dists[i][toks[i]].item()) for i in range(n)]
    uniforms = [float(torch.rand(1).item()) for _ in range(n)]
    n_ok = accept_prefix_len(d_probs, t_probs, uniforms)
    out = toks[:n_ok]
    if n_ok < n:
        out.append(_sample_residual(p_dists[n_ok], q_dists[n_ok]))
        return out, 1
    out.append(int(torch.multinomial(bonus, 1).item()))
    return out, 1


def decode_spec(
    student: Any,
    teacher: Any,
    tokenizer: Any,
    prompt: str,
    *,
    draft_len: int,
    max_new_tokens: int,
    temperature: float,
    top_p: float,
    seed: int,
    device: torch.device,
) -> DecodeResult:
    if draft_len < 1:
        raise ValueError("draft_len must be >= 1")
    torch.manual_seed(seed)
    if device.type == "cuda":
        torch.cuda.manual_seed_all(seed)
    ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
    prompt_len = int(ids.shape[1])
    n_new = 0
    token_evals = 0
    t0 = time.perf_counter()
    while n_new < max_new_tokens:
        d = min(draft_len, max_new_tokens - n_new)
        drafted, q_dists, toks, ev = _draft_block(
            student, ids, d, temperature=temperature, top_p=top_p
        )
        token_evals += ev
        committed, tev = _verify(teacher, drafted, q_dists, toks)
        token_evals += tev
        for tok in committed:
            if n_new >= max_new_tokens:
                break
            ids = torch.cat(
                [ids, torch.tensor([[tok]], device=device, dtype=ids.dtype)],
                dim=1,
            )
            n_new += 1
            if tok == tokenizer.eos_token_id:
                n_new = max_new_tokens
                break
    if device.type == "cuda":
        torch.cuda.synchronize()
    wall_ms = (time.perf_counter() - t0) * 1000.0
    new_ids = tuple(int(x) for x in ids[0, prompt_len:].tolist())
    text = tokenizer.decode(list(new_ids), skip_special_tokens=True)
    return DecodeResult(
        token_ids=new_ids,
        text=text,
        mean_logprob=mean_logprob([0.0] * len(new_ids)) if new_ids else float("-inf"),
        wall_ms=wall_ms,
        token_evals=token_evals,
    )
