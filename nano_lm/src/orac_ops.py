"""H-ORAC: teacher-oracle tip pick; dual gate vs EARLY/DECM."""

from __future__ import annotations

from typing import Mapping, Sequence

from lat_ops import EPS_LP

__all__ = ["oracle_pick", "decide_horac"]


def oracle_pick(scores: Sequence[float]) -> int:
    """
    GIVEN tip scores (higher better)
    WHEN oracle-picking
    THEN return argmax index; ties keep lowest index.
    """
    if not scores:
        raise ValueError("oracle_pick: scores must be non-empty")
    best_i = 0
    best_v = float(scores[0])
    for i in range(1, len(scores)):
        v = float(scores[i])
        if v > best_v:
            best_i = i
            best_v = v
    return best_i


def decide_horac(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-ORAC vs H-EARLY and H-DECM tips
    WHEN deciding
    THEN PROMOTE only if lp ≥ max(tips)−ε and wall < min(tips); else KILL.
    """
    early = stats.get("H-EARLY")
    decm = stats.get("H-DECM")
    if early is None or decm is None:
        return "needs H-EARLY+H-DECM controls"
    max_lp = max(float(early["mean_lp"]), float(decm["mean_lp"]))
    min_wall = min(float(early["mean_wall"]), float(decm["mean_wall"]))
    if float(s["mean_lp"]) < max_lp - EPS_LP:
        return "KILL (≤ max tip quality)"
    if not (float(s["mean_wall"]) < min_wall):
        return "KILL (no dual wall win)"
    return "PROMOTE (oracle dual win)"
