"""H-TIE: tied embed + shared transformer block; dual gate vs H-STAG."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "TIP_STAGES",
    "decide_htie",
    "EPS_LP",
]

TIP_STAGES = 4


def decide_htie(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-TIE vs H-STAG tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ STAG−ε and (params < STAG or gflops < STAG).
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-STAG)"
    param_win = float(s["mean_params"]) < float(tip["mean_params"])
    flop_win = float(s["mean_gflops"]) < float(tip["mean_gflops"])
    if not (param_win or flop_win):
        return "KILL (no param/FLOP win vs H-STAG)"
    return "PROMOTE (tied+share vs STAG)"
