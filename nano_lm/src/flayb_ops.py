"""H-FLAYB: LAY under FCPOOLB dual-budget batch; tok/s|wall vs H-FCPOOLB."""

from __future__ import annotations

from typing import Mapping

from fcpoolb_ops import FCPOOLB_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hflayb", "FLAYB_CHUNK", "EPS_LP"]

FLAYB_CHUNK = FCPOOLB_CHUNK


def decide_hflayb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-FLAYB vs H-FCPOOLB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and (tok/s > FCPOOLB or wall < FCPOOLB); else KILL.
    """
    tip = stats.get("H-FCPOOLB")
    if tip is None:
        return "needs H-FCPOOLB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-FCPOOLB)"
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    if not (tps_win or wall_win):
        return "KILL (no tok/s/wall win vs H-FCPOOLB)"
    return "PROMOTE (LAY under FCPOOLB batch)"
