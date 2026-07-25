"""H-LAYB: LAY early-exit under FUSEB dual-budget batch; tok/s|wall vs H-FUSEB."""

from __future__ import annotations

from typing import Mapping

from chbat_ops import CHBAT_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hlayb", "LAYB_CHUNK", "EPS_LP"]

LAYB_CHUNK = CHBAT_CHUNK


def decide_hlayb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-LAYB vs H-FUSEB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and (tok/s > FUSEB or wall < FUSEB); else KILL.
    """
    tip = stats.get("H-FUSEB")
    if tip is None:
        return "needs H-FUSEB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-FUSEB)"
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    if not (tps_win or wall_win):
        return "KILL (no tok/s/wall win vs H-FUSEB)"
    return "PROMOTE (LAY under FUSEB batch)"
