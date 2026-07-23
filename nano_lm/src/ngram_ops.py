"""H-NGRAM: no-repeat n-gram decode helpers; dual gate vs B4."""

from __future__ import annotations

from typing import Mapping, Sequence

import torch

from lat_ops import EPS_LP

__all__ = [
    "NGRAM_SIZES",
    "banned_next_tokens",
    "apply_ngram_ban",
    "decide_hngram",
    "best_ngram_index",
]

# 0 = identity (no ban); HF-style sizes otherwise.
NGRAM_SIZES = (0, 2, 3, 4)


def banned_next_tokens(prev_ids: Sequence[int], ngram_size: int) -> set[int]:
    """
    GIVEN previous token ids and ngram_size
    WHEN ngram_size >= 2 and enough history
    THEN return tokens that would complete a repeated n-gram; else empty.
    """
    n = int(ngram_size)
    if n < 2:
        return set()
    ids = [int(x) for x in prev_ids]
    if len(ids) < n - 1:
        return set()
    prefix = tuple(ids[-(n - 1) :])
    banned: set[int] = set()
    for i in range(len(ids) - n + 1):
        if tuple(ids[i : i + n - 1]) == prefix:
            banned.add(ids[i + n - 1])
    return banned


def apply_ngram_ban(
    logits: torch.Tensor, prev_ids: torch.Tensor, ngram_size: int
) -> torch.Tensor:
    """
    GIVEN logits [B,V] and previous ids [B,T]
    WHEN applying no-repeat n-gram
    THEN set banned next-token logits to -inf; size 0 is identity.
    """
    n = int(ngram_size)
    if n < 0:
        raise ValueError("apply_ngram_ban: ngram_size must be >= 0")
    if n == 0:
        return logits
    out = logits.clone()
    for b in range(int(out.shape[0])):
        for tid in banned_next_tokens(prev_ids[b].tolist(), n):
            out[b, tid] = float("-inf")
    return out


def decide_hngram(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-NGRAM vs B4
    WHEN deciding
    THEN PROMOTE only if quality ≥ B4−ε and wall < B4; else KILL.
    """
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if float(s["mean_lp"]) < float(b4["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs B4)"
    if not (float(s["mean_wall"]) < float(b4["mean_wall"])):
        return "KILL (no speedup vs B4)"
    return "PROMOTE (quality@wall vs B4)"


def best_ngram_index(scores: Sequence[float]) -> int:
    """Argmax over grid scores; ties keep lowest index."""
    if not scores:
        raise ValueError("best_ngram_index: empty")
    best_i = 0
    best_v = float(scores[0])
    for i in range(1, len(scores)):
        v = float(scores[i])
        if v > best_v:
            best_i = i
            best_v = v
    return best_i
