"""H-SKIP: BAT→CHBAT (skip CBAT FLAG) honest throughput path."""

from __future__ import annotations

from typing import Mapping

from chbat_ops import CHBAT_CHUNK
from lat_ops import EPS_LP
from pareto_ops import DELTA_GFLOPS_FRAC

__all__ = [
    "decide_hskip",
    "gflops_beyond_tip",
    "SKIP_CHUNK",
    "DELTA_GFLOPS_FRAC",
    "EPS_LP",
]

SKIP_CHUNK = CHBAT_CHUNK


def gflops_beyond_tip(
    util: Mapping[str, float],
    tip: Mapping[str, float],
    *,
    delta_frac: float = DELTA_GFLOPS_FRAC,
) -> bool:
    """
    GIVEN util and tip mean_gflops
    WHEN checking GFLOPs honesty
    THEN True iff util GFLOPs > tip·(1+δ).
    """
    tip_gf = float(tip["mean_gflops"])
    util_gf = float(util["mean_gflops"])
    return bool(util_gf > tip_gf * (1.0 + float(delta_frac)))


def decide_hskip(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    delta_frac: float = DELTA_GFLOPS_FRAC,
) -> str:
    """
    GIVEN H-SKIP (CHB chunk under BAT) vs H-BAT
    WHEN deciding
    THEN KILL iff no wall/tok/s win or GFLOPs > BAT·(1+δ); else PROMOTE.
    """
    tip = stats.get("H-BAT")
    if tip is None:
        return "needs H-BAT control"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    if not (wall_win or tps_win):
        return "KILL (no wall/tok/s win vs H-BAT)"
    if gflops_beyond_tip(s, tip, delta_frac=delta_frac):
        return "KILL (GFLOPs↑ beyond tip+δ vs H-BAT)"
    return "PROMOTE (BAT→CHBAT skip CBAT; honest GFLOPs)"
