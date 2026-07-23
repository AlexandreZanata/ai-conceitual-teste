"""Goldilocks fitness helpers for H-GLD: reward mid band, punish extremes."""

from __future__ import annotations

from typing import Sequence


def goldilocks_score(raw: float, *, mid: float, width: float) -> float:
    """
    GIVEN raw fitness (e.g. teacher_lp) and band (mid, width>0)
    WHEN scoring Goldilocks preference
    THEN return −|raw−mid|/width (peaks at mid; extremes worse).
    """
    if width <= 0.0:
        raise ValueError("goldilocks_score: width must be > 0")
    return -abs(raw - mid) / width


def goldilocks_scores(
    raws: Sequence[float], *, mid: float, width: float
) -> list[float]:
    """Map a list of raw fitnesses through goldilocks_score."""
    return [goldilocks_score(r, mid=mid, width=width) for r in raws]
