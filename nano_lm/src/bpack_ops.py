"""H-BPACK: freeze SKIP + LAYB throughput packs vs tip H-EARLY."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from layb_ops import LAYB_CHUNK
from skip_ops import SKIP_CHUNK, gflops_beyond_tip

__all__ = [
    "decide_hbpack",
    "BPACK_CHUNK",
    "SKIP_CHUNK",
    "EPS_LP",
]

BPACK_CHUNK = LAYB_CHUNK


def _speed_win(s: Mapping[str, float], tip: Mapping[str, float]) -> bool:
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    return bool(wall_win or tps_win)


def decide_hbpack(
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-EARLY + H-SKIP + H-LAYB
    WHEN freezing throughput packs vs tip
    THEN PROMOTE iff both packs have |Δlp|≤ε and wall/tok/s win;
         SKIP also must not inflate GFLOPs beyond EARLY·(1+δ).
    """
    early = stats.get("H-EARLY")
    skip = stats.get("H-SKIP")
    layb = stats.get("H-LAYB")
    if early is None or skip is None or layb is None:
        return "needs H-EARLY, H-SKIP, and H-LAYB"
    if abs(float(skip["mean_lp"]) - float(early["mean_lp"])) > float(eps_lp):
        return "KILL (SKIP lp change vs H-EARLY)"
    if not _speed_win(skip, early):
        return "KILL (SKIP no wall/tok/s win vs H-EARLY)"
    if gflops_beyond_tip(skip, early):
        return "KILL (SKIP GFLOPs↑ beyond tip+δ vs H-EARLY)"
    if abs(float(layb["mean_lp"]) - float(early["mean_lp"])) > float(eps_lp):
        return "KILL (LAYB lp change vs H-EARLY)"
    if not _speed_win(layb, early):
        return "KILL (LAYB no wall/tok/s win vs H-EARLY)"
    return "PROMOTE (SKIP+LAYB throughput packs vs EARLY)"
