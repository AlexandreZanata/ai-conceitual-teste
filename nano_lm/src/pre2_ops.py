"""H-PRE2: 2-deep H2D prefetch under ADAMF; ms/step vs H-ADAMF."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hpre2", "EPS_LP"]


def decide_hpre2(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-PRE2 vs H-ADAMF
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and ms/step < ADAMF; else KILL.
    """
    tip = stats.get("H-ADAMF")
    if tip is None:
        return "needs H-ADAMF control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-ADAMF)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs H-ADAMF)"
    return "PROMOTE (2-deep prefetch under ADAMF)"
