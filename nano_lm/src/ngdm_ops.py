"""H-NGDM: NGRAM × DECM tip stack; dual gate vs max tip."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hngdm", "tip_max_lp", "tip_min_wall"]

_TIPS = ("H-NGRAM", "H-DECM")


def tip_max_lp(stats: Mapping[str, Mapping[str, float]]) -> float | None:
    vals = [float(stats[t]["mean_lp"]) for t in _TIPS if t in stats]
    return max(vals) if vals else None


def tip_min_wall(stats: Mapping[str, Mapping[str, float]]) -> float | None:
    vals = [float(stats[t]["mean_wall"]) for t in _TIPS if t in stats]
    return min(vals) if vals else None


def decide_hngdm(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-NGDM vs H-NGRAM and H-DECM
    WHEN deciding
    THEN PROMOTE only if lp ≥ max(tips)−ε and wall < min(tips); else KILL.
    """
    if any(t not in stats for t in _TIPS):
        return "needs H-NGRAM+H-DECM controls"
    max_lp = tip_max_lp(stats)
    min_wall = tip_min_wall(stats)
    assert max_lp is not None and min_wall is not None
    if float(s["mean_lp"]) < max_lp - EPS_LP:
        return "KILL (≤ max tip quality)"
    if not (float(s["mean_wall"]) < min_wall):
        return "KILL (no dual wall win)"
    return "PROMOTE (dual win vs tips)"
