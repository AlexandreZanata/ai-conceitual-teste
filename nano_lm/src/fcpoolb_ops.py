"""H-FCPOOLB: FUSE (FLASH⊕KVSEL) under CPOOLB; tok/s|wall vs H-CPOOLB."""

from __future__ import annotations

from typing import Mapping

from cpoolb_ops import CPOOLB_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hfcpoolb", "FCPOOLB_CHUNK", "EPS_LP"]

# CHB tip B under quality batch (same as CPOOLB); FUSE gates KV on/off per budget.
FCPOOLB_CHUNK = CPOOLB_CHUNK


def decide_hfcpoolb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-FCPOOLB vs H-CPOOLB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and (tok/s > CPOOLB or wall < CPOOLB); else KILL.
    """
    tip = stats.get("H-CPOOLB")
    if tip is None:
        return "needs H-CPOOLB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-CPOOLB)"
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    if not (tps_win or wall_win):
        return "KILL (no tok/s/wall win vs H-CPOOLB)"
    return "PROMOTE (FUSE under CPOOLB batch)"
