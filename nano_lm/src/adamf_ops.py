"""H-ADAMF: fused AdamW under HALF train; ms/step vs H-HALF."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hadamf", "EPS_LP"]


def decide_hadamf(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-ADAMF vs H-HALF
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and ms/step < HALF; else KILL.
    """
    tip = stats.get("H-HALF")
    if tip is None:
        return "needs H-HALF control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-HALF)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs H-HALF)"
    return "PROMOTE (fused AdamW under HALF)"
