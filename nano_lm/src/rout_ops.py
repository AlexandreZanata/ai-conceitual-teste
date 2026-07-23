"""H-ROUT: confidence router EARLY vs DECM tip genes; dual gate vs tips."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["DEFAULT_TAU", "route_tip", "decide_hrout"]

DEFAULT_TAU = 0.35


def route_tip(confidence: float, *, tau: float = DEFAULT_TAU) -> str:
    """
    GIVEN prompt-top confidence in [0,1] and threshold tau
    WHEN routing between tip policies
    THEN return "early" if confidence >= tau else "decm".
    """
    if not (0.0 <= float(tau) <= 1.0):
        raise ValueError("route_tip: tau must be in [0,1]")
    return "early" if float(confidence) >= float(tau) else "decm"


def decide_hrout(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-ROUT vs H-EARLY and H-DECM tips
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
    return "PROMOTE (dual win vs tips)"
