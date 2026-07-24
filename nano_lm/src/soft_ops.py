"""H-SOFT: offline soft-label cache; train step-time gate vs live STAG."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hsoft", "ms_per_step"]


def ms_per_step(*, wall_s: float, steps: int) -> float:
    """
    GIVEN train wall seconds and step count
    WHEN computing step time
    THEN return milliseconds per step (0 if steps < 1).
    """
    if int(steps) < 1:
        return 0.0
    return 1000.0 * float(wall_s) / float(steps)


def decide_hsoft(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-SOFT vs live H-STAG control
    WHEN deciding
    THEN PROMOTE iff lp ≥ STAG−ε and ms/step < STAG; else KILL.
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-STAG)"
    if float(s["mean_ms_step"]) >= float(tip["mean_ms_step"]):
        return "KILL (no train step-time win vs live STAG)"
    return "PROMOTE (soft-label cache vs live STAG)"
