"""H-PRUNB: PRUN ckpt under LAYB decode; wall|GFLOPs vs H-LAYB."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from layb_ops import LAYB_CHUNK

__all__ = ["decide_hprunb", "PRUNB_CHUNK", "EPS_LP"]

PRUNB_CHUNK = LAYB_CHUNK


def decide_hprunb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-PRUNB vs H-LAYB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and (wall < LAYB or GFLOPs < LAYB); else KILL.
    """
    tip = stats.get("H-LAYB")
    if tip is None:
        return "needs H-LAYB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-LAYB)"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    gf_win = float(s["mean_gflops"]) < float(tip["mean_gflops"])
    if not (wall_win or gf_win):
        return "KILL (no wall/gflops win vs H-LAYB)"
    return "PROMOTE (PRUN ckpt under LAYB decode)"
