"""H-BAND: UCB1 arm selection over fixed decode genes."""

from __future__ import annotations

import math
from typing import Mapping, Sequence

__all__ = ["ucb1_select", "decide_hband"]


def ucb1_select(
    means: Sequence[float],
    counts: Sequence[int],
    *,
    total_pulls: int,
    c: float = math.sqrt(2.0),
) -> int:
    """
    GIVEN arm means/counts and pulls completed so far
    WHEN choosing next arm
    THEN return UCB1 index (unpulled arms preferred; ties → lower index).
    """
    if len(means) != len(counts) or not means:
        raise ValueError("ucb1_select: means/counts length mismatch or empty")
    if total_pulls < 0:
        raise ValueError("ucb1_select: total_pulls must be >= 0")
    t = max(1, int(total_pulls))
    best_i = 0
    best_s = float("-inf")
    for i, (m, n) in enumerate(zip(means, counts)):
        if int(n) <= 0:
            score = float("inf")
        else:
            score = float(m) + float(c) * math.sqrt(math.log(t) / float(n))
        if score > best_s + 1e-15:
            best_s = score
            best_i = i
    return best_i


def decide_hband(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-BAND stats vs H-CASC / H-DECK
    WHEN deciding
    THEN KILL if ≤ max(available controls); else PROMOTE.
    """
    bars = [
        float(stats[name]["mean_lp"])
        for name in ("H-CASC", "H-DECK")
        if name in stats
    ]
    if not bars:
        return "needs H-CASC or H-DECK control"
    bar = max(bars)
    if float(s["mean_lp"]) <= bar + 1e-6:
        return "KILL (≤ H-DECK / H-CASC)"
    return "PROMOTE (beats H-DECK/H-CASC)"
