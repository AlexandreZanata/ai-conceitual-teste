"""H-DECKL: DECK search + latency-aware claim; Pareto vs B4/H-CASC."""

from __future__ import annotations

from typing import Mapping

__all__ = ["dominates_lp_wall", "decide_hdeckl"]


def dominates_lp_wall(
    a_lp: float, a_wall: float, b_lp: float, b_wall: float
) -> bool:
    """
    GIVEN two (lp, wall_ms) points (higher lp better, lower wall better)
    WHEN comparing
    THEN True iff A Pareto-dominates B.
    """
    ge_lp = float(a_lp) >= float(b_lp) - 1e-12
    le_wall = float(a_wall) <= float(b_wall) + 1e-12
    strict = (float(a_lp) > float(b_lp) + 1e-12) or (
        float(a_wall) < float(b_wall) - 1e-12
    )
    return ge_lp and le_wall and strict


def decide_hdeckl(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DECKL (lp, wall) vs B4 / optional H-CASC
    WHEN deciding
    THEN KILL if dominated on Pareto; else PROMOTE.
    """
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    s_lp, s_wall = float(s["mean_lp"]), float(s["mean_wall"])
    b4_lp, b4_wall = float(b4["mean_lp"]), float(b4["mean_wall"])
    if dominates_lp_wall(b4_lp, b4_wall, s_lp, s_wall):
        return "KILL (dominated on Pareto by B4)"
    casc = stats.get("H-CASC")
    if casc is not None:
        c_wall = float(casc.get("mean_wall", float("nan")))
        if c_wall == c_wall and dominates_lp_wall(
            float(casc["mean_lp"]), c_wall, s_lp, s_wall
        ):
            return "KILL (dominated on Pareto by H-CASC)"
    if dominates_lp_wall(s_lp, s_wall, b4_lp, b4_wall):
        return "PROMOTE (Pareto-dominates B4)"
    return "PROMOTE (Pareto non-dominated vs B4)"
