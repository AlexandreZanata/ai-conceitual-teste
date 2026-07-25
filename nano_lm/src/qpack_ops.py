"""H-QPACK: freeze FLAYB quality pack vs tip H-POOL."""

from __future__ import annotations

from typing import Mapping

from flayb_ops import FLAYB_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hqpack", "QPACK_CHUNK", "EPS_LP"]

QPACK_CHUNK = FLAYB_CHUNK


def decide_hqpack(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-FLAYB quality pack vs tip H-POOL
    WHEN deciding card hygiene
    THEN PROMOTE iff lp ≥ POOL−ε and (wall < POOL or tok/s > POOL).
    """
    tip = stats.get("H-POOL")
    if tip is None:
        return "needs H-POOL control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (FLAYB quality drop vs H-POOL)"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    if not (wall_win or tps_win):
        return "KILL (FLAYB no wall/tok/s win vs H-POOL)"
    return "PROMOTE (FLAYB quality pack vs POOL)"
