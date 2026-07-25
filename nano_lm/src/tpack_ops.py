"""H-TPACK: freeze PRE3 train I/O pack vs tip H-STAG on ms/step only."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_htpack", "EPS_LP"]


def decide_htpack(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-TPACK (PRE3 stack train) vs live H-STAG
    WHEN deciding (ms/step only; not e2e)
    THEN PROMOTE iff lp ≥ STAG−ε and ms/step < STAG; else KILL.
    Note: |Δlp| kill = quality drop below tip−ε (paths differ; abs equality N/A).
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-STAG)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs H-STAG)"
    return "PROMOTE (PRE3 ms/step pack vs live STAG; not e2e)"
