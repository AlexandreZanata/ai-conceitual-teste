"""H-PRUNF: PRUN ckpt under FLAYB decode; wall|GFLOPs vs H-FLAYB."""

from __future__ import annotations

from typing import Mapping

from flayb_ops import FLAYB_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hprunf", "PRUNF_CHUNK", "EPS_LP"]

PRUNF_CHUNK = FLAYB_CHUNK


def decide_hprunf(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-PRUNF vs H-FLAYB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and (wall < FLAYB or GFLOPs < FLAYB); else KILL.
    """
    tip = stats.get("H-FLAYB")
    if tip is None:
        return "needs H-FLAYB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-FLAYB)"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    gf_win = float(s["mean_gflops"]) < float(tip["mean_gflops"])
    if not (wall_win or gf_win):
        return "KILL (no wall/gflops win vs H-FLAYB)"
    return "PROMOTE (PRUN ckpt under FLAYB decode)"
