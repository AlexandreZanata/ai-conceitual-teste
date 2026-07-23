"""H-PARE: Pareto archive of (lp, wall) genes; pick knee point."""

from __future__ import annotations

from typing import Mapping, Sequence

from deckl_ops import dominates_lp_wall

__all__ = [
    "pareto_indices",
    "pick_knee",
    "decide_hpare",
]


def pareto_indices(lps: Sequence[float], walls: Sequence[float]) -> list[int]:
    """
    GIVEN equal-length lp (↑ better) and wall_ms (↓ better)
    WHEN computing the front
    THEN return indices of non-dominated points (stable by input order).
    """
    if len(lps) != len(walls):
        raise ValueError("pareto_indices: length mismatch")
    if not lps:
        return []
    out: list[int] = []
    for i, (lp_i, w_i) in enumerate(zip(lps, walls)):
        dominated = False
        for j, (lp_j, w_j) in enumerate(zip(lps, walls)):
            if i == j:
                continue
            if dominates_lp_wall(lp_j, w_j, lp_i, w_i):
                dominated = True
                break
        if not dominated:
            out.append(i)
    return out


def pick_knee(lps: Sequence[float], walls: Sequence[float]) -> int:
    """
    GIVEN non-empty (lp, wall) lists
    WHEN choosing the knee
    THEN return index closest to utopia (max_lp, min_wall) in unit square.
    """
    if not lps or len(lps) != len(walls):
        raise ValueError("pick_knee: need equal non-empty lp/wall")
    max_lp, min_lp = max(lps), min(lps)
    max_w, min_w = max(walls), min(walls)
    best_i, best_d = 0, float("inf")
    for i, (lp, w) in enumerate(zip(lps, walls)):
        nx = 0.5 if max_lp <= min_lp else (lp - min_lp) / (max_lp - min_lp)
        # wall: lower better → invert
        ny = 0.5 if max_w <= min_w else (max_w - w) / (max_w - min_w)
        dist = (1.0 - nx) ** 2 + (1.0 - ny) ** 2
        if dist < best_d - 1e-15:
            best_d = dist
            best_i = i
    return best_i


def decide_hpare(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-PARE (lp, wall, front_n) vs B4
    WHEN deciding
    THEN KILL if empty front or dominated / ≤ B4; else PROMOTE.
    """
    if float(s.get("front_n", 0.0)) <= 0.0:
        return "KILL (empty Pareto front)"
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    s_lp, s_wall = float(s["mean_lp"]), float(s["mean_wall"])
    b4_lp, b4_wall = float(b4["mean_lp"]), float(b4["mean_wall"])
    if dominates_lp_wall(b4_lp, b4_wall, s_lp, s_wall):
        return "KILL (≤ B4 / dominated on Pareto)"
    if dominates_lp_wall(s_lp, s_wall, b4_lp, b4_wall):
        return "PROMOTE (Pareto-dominates B4)"
    return "PROMOTE (Pareto non-dominated vs B4)"
