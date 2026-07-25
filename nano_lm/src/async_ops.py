"""H-ASYNC: overlap TOP cache build with PIN train; e2e wall gate."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hasync", "e2e_wall_s", "EPS_LP"]


def e2e_wall_s(*, cache_build_s: float, train_wall_s: float) -> float:
    """Sequential end-to-end wall (cache then train)."""
    return float(cache_build_s) + float(train_wall_s)


def decide_hasync(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-ASYNC vs H-PIN control
    WHEN deciding
    THEN PROMOTE iff lp ≥ PIN−ε and e2e_wall < PIN; else KILL.
    """
    tip = stats.get("H-PIN")
    if tip is None:
        return "needs H-PIN control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-PIN)"
    if float(s["mean_e2e_wall"]) >= float(tip["mean_e2e_wall"]):
        return "KILL (no end-to-end train wall win vs H-PIN)"
    return "PROMOTE (async cache∩PIN train overlap)"
