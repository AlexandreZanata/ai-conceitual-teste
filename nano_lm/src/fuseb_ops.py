"""H-FUSEB: FUSE (FLASH⊕KVSEL) under CHBAT batch; tok/s|wall vs H-CHBAT."""

from __future__ import annotations

from typing import Mapping

from chbat_ops import CHBAT_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hfuseb", "FUSEB_CHUNK", "EPS_LP"]

# CHB tip B under batch (same as CHBAT); FUSE gates KV on/off per budget.
FUSEB_CHUNK = CHBAT_CHUNK


def decide_hfuseb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-FUSEB vs H-CHBAT
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and (tok/s > CHBAT or wall < CHBAT); else KILL.
    """
    tip = stats.get("H-CHBAT")
    if tip is None:
        return "needs H-CHBAT control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-CHBAT)"
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    if not (tps_win or wall_win):
        return "KILL (no tok/s/wall win vs H-CHBAT)"
    return "PROMOTE (FUSE under CHBAT batch)"
