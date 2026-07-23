"""H-BLK: block-parallel decode decision helpers vs B3."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["CLIFF_LP", "BLOCK_SIZES", "decide_hblk"]

CLIFF_LP = 0.5
BLOCK_SIZES = (2, 4, 8)


def decide_hblk(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-BLK vs B3 (AR decode)
    WHEN deciding
    THEN KILL on quality crash/drop or no wall win; else PROMOTE.
    """
    b3 = stats.get("B3")
    if b3 is None:
        return "needs B3 control"
    delta = float(s["mean_lp"]) - float(b3["mean_lp"])
    if delta < -CLIFF_LP:
        return "KILL (quality crash)"
    if delta < -EPS_LP:
        return "KILL (quality drop vs B3)"
    if not (float(s["mean_wall"]) < float(b3["mean_wall"])):
        return "KILL (no speedup vs B3)"
    return "PROMOTE (block parallel quality@wall vs B3)"
