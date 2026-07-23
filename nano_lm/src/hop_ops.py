"""H-HOP: continuous Hopfield retrieve + mix; decide vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

__all__ = [
    "hopfield_retrieve",
    "mix_hidden",
    "push_patterns",
    "decide_hhop",
]


def hopfield_retrieve(
    query: torch.Tensor, patterns: torch.Tensor, *, beta: float
) -> torch.Tensor:
    """
    GIVEN query [..., d] and patterns [M, d]
    WHEN retrieving (modern Hopfield)
    THEN return softmax(β q pᵀ) p with same leading shape as query.
    """
    if beta <= 0.0:
        raise ValueError("hopfield_retrieve: beta must be > 0")
    if patterns.ndim != 2:
        raise ValueError("hopfield_retrieve: patterns must be [M,d]")
    if patterns.shape[0] < 1:
        raise ValueError("hopfield_retrieve: empty patterns")
    flat = query.reshape(-1, query.shape[-1])
    scores = float(beta) * (flat @ patterns.transpose(0, 1))
    weights = F.softmax(scores, dim=-1)
    out = weights @ patterns
    return out.reshape(query.shape)


def mix_hidden(
    hidden: torch.Tensor, retrieved: torch.Tensor, *, alpha: float
) -> torch.Tensor:
    """
    GIVEN hidden and retrieved states
    WHEN mixing with prior strength α
    THEN return hidden + α · retrieved.
    """
    if alpha < 0.0:
        raise ValueError("mix_hidden: alpha must be >= 0")
    return hidden + float(alpha) * retrieved


def push_patterns(
    bank: torch.Tensor, vectors: torch.Tensor, *, cursor: int
) -> int:
    """
    GIVEN a circular bank [M,d] and vectors [N,d]
    WHEN storing detached rows
    THEN write into bank and return next cursor.
    """
    if bank.ndim != 2 or vectors.ndim != 2:
        raise ValueError("push_patterns: bank/vectors must be 2D")
    if bank.shape[1] != vectors.shape[1]:
        raise ValueError("push_patterns: dim mismatch")
    m = int(bank.shape[0])
    with torch.no_grad():
        for row in vectors.detach():
            bank[cursor % m].copy_(row)
            cursor = (cursor + 1) % m
    return int(cursor)


def decide_hhop(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-HOP vs B2
    WHEN deciding
    THEN PROMOTE only if teacher_lp > B2; else KILL (no gain vs AR/KD).
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (no gain vs B2)"
