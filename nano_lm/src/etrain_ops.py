"""H-ETRAIN: PRE3 e2e train wall (cache+train) vs live H-STAG."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hetrain", "e2e_wall_s", "EPS_LP"]


def e2e_wall_s(*, cache_build_s: float, train_wall_s: float) -> float:
    """
    GIVEN cache build seconds and train wall seconds
    WHEN computing end-to-end train cost
    THEN return cache_build + train (live STAG uses cache_build=0).
    """
    return float(cache_build_s) + float(train_wall_s)


def decide_hetrain(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-ETRAIN (PRE3 stack e2e) vs H-STAG live
    WHEN deciding
    THEN PROMOTE iff lp ≥ STAG−ε and e2e_wall < STAG; else KILL.
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-STAG)"
    if not (float(s["mean_e2e"]) < float(tip["mean_e2e"])):
        return "KILL (no end-to-end train wall win vs H-STAG)"
    return "PROMOTE (PRE3 e2e vs live STAG)"
