"""H-ROUTE: short→GALL, long→GRAPHF; vs best single arm."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from serve_ops import SERVE_CHUNK

__all__ = [
    "decide_hroute",
    "arm_dominates",
    "ROUTE_CHUNK",
    "EPS_LP",
]

ROUTE_CHUNK = SERVE_CHUNK


def arm_dominates(
    arm: Mapping[str, float],
    route: Mapping[str, float],
    *,
    eps_lp: float = EPS_LP,
) -> bool:
    """
    GIVEN single-arm metrics and ROUTE metrics
    WHEN checking Pareto dominance on (lp, wall)
    THEN True iff arm is ≥route on lp−ε and ≤route on wall with a strict win.
    """
    lp_ok = float(arm["mean_lp"]) >= float(route["mean_lp"]) - float(eps_lp)
    wall_ok = float(arm["mean_wall"]) <= float(route["mean_wall"])
    better = (float(arm["mean_lp"]) > float(route["mean_lp"]) + float(eps_lp)) or (
        float(arm["mean_wall"]) < float(route["mean_wall"])
    )
    return bool(lp_ok and wall_ok and better)


def decide_hroute(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-ROUTE vs H-GALL and H-GRAPHF single arms
    WHEN deciding
    THEN KILL iff either arm dominates ROUTE on (lp, wall); else PROMOTE.
    """
    gall = stats.get("H-GALL")
    graphf = stats.get("H-GRAPHF")
    if gall is None or graphf is None:
        return "needs H-GALL and H-GRAPHF controls"
    if arm_dominates(gall, s, eps_lp=eps_lp):
        return "KILL (dominated by H-GALL)"
    if arm_dominates(graphf, s, eps_lp=eps_lp):
        return "KILL (dominated by H-GRAPHF)"
    return "PROMOTE (length-budget router not dominated)"
