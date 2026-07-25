"""H-PRE3: 3-deep H2D prefetch under PRE2; ms/step vs H-PRE2."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hpre3", "EPS_LP"]


def decide_hpre3(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-PRE3 vs H-PRE2
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and ms/step < PRE2; else KILL.
    """
    tip = stats.get("H-PRE2")
    if tip is None:
        return "needs H-PRE2 control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-PRE2)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs H-PRE2)"
    return "PROMOTE (3-deep prefetch under PRE2)"
