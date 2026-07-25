"""H-PACK: freeze SERVE=min-wall and SROUTE=Pareto packs vs H-EARLY."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from serve_ops import SERVE_CHUNK

__all__ = ["decide_hpack", "PACK_CHUNK", "EPS_LP"]

PACK_CHUNK = SERVE_CHUNK


def _speed_win(s: Mapping[str, float], tip: Mapping[str, float]) -> bool:
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    return bool(wall_win or tps_win)


def decide_hpack(
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-EARLY tip + frozen H-SERVE (min-wall) + H-SROUTE (Pareto)
    WHEN deciding card hygiene
    THEN PROMOTE iff both packs beat EARLY on wall/tok/s with quality floor;
         SERVE also requires |Δlp|≤ε; SROUTE requires lp ≥ EARLY−ε.
    """
    early = stats.get("H-EARLY")
    serve = stats.get("H-SERVE")
    sroute = stats.get("H-SROUTE")
    if early is None or serve is None or sroute is None:
        return "needs H-EARLY, H-SERVE, and H-SROUTE"
    if abs(float(serve["mean_lp"]) - float(early["mean_lp"])) > float(eps_lp):
        return "KILL (SERVE lp change vs H-EARLY)"
    if not _speed_win(serve, early):
        return "KILL (SERVE no wall/tok/s win vs H-EARLY)"
    if float(sroute["mean_lp"]) < float(early["mean_lp"]) - float(eps_lp):
        return "KILL (SROUTE quality drop vs H-EARLY)"
    if not _speed_win(sroute, early):
        return "KILL (SROUTE no wall/tok/s win vs H-EARLY)"
    return "PROMOTE (SERVE=min-wall + SROUTE=Pareto packs vs EARLY)"
