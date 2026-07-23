"""Latency-aware fitness for H-LAT (smarter+faster decode genes)."""

from __future__ import annotations

import math
from typing import Mapping

EPS_LP = 0.05


def latency_aware_score(lp: float, wall_ms: float, lam: float) -> float:
    """
    GIVEN teacher log-prob and mean wall_ms
    WHEN combining with λ ≥ 0
    THEN return lp − λ · log1p(wall_ms).
    """
    if lam < 0.0:
        raise ValueError("latency_aware_score: lam must be >= 0")
    return float(lp) - float(lam) * math.log1p(max(0.0, float(wall_ms)))


def decide_hlat(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-LAT vs B4 (and optional H-DEC)
    WHEN deciding
    THEN PROMOTE only if quality ≥ B4−ε and wall < B4; else KILL.
    """
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if float(s["mean_lp"]) < float(b4["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs B4)"
    if not (float(s["mean_wall"]) < float(b4["mean_wall"])):
        return "KILL (no speedup vs B4)"
    hdec = stats.get("H-DEC")
    if hdec is not None:
        worse_q = float(s["mean_lp"]) < float(hdec["mean_lp"]) - EPS_LP
        slower = float(s["mean_wall"]) >= float(hdec["mean_wall"])
        if worse_q and slower:
            return "KILL (dominated by H-DEC)"
    return "PROMOTE (quality@wall vs B4)"
