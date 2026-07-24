"""H-DEPTH: STAG train with 1 fewer layer, then PRUN recover."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "TIP_LAYERS",
    "DEPTH_LAYERS",
    "decide_hdepth",
    "EPS_LP",
]

TIP_LAYERS = 2
DEPTH_LAYERS = 1


def decide_hdepth(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-DEPTH vs H-STAG tip (same EARLY decode)
    WHEN deciding
    THEN PROMOTE iff lp ≥ STAG−ε and wall < STAG.
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-STAG)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-STAG)"
    return "PROMOTE (shallow STAG+PRUN vs tip)"
