"""H-PRE: double-buffer H2D prefetch under PIN; ms/step vs H-PIN."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hpre", "EPS_LP"]


def decide_hpre(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-PRE vs H-PIN
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and ms/step < PIN; else KILL.
    """
    tip = stats.get("H-PIN")
    if tip is None:
        return "needs H-PIN control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-PIN)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs H-PIN)"
    return "PROMOTE (prefetch H2D under PIN)"
