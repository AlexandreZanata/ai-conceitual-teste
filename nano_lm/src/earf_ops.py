"""H-EARF: FLOP-aware early-exit fitness score + decide vs H-EARLY."""

from __future__ import annotations

import math
from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["flop_aware_score", "decide_hearf", "EPS_LP"]


def flop_aware_score(lp: float, gflops: float, lam: float) -> float:
    """
    GIVEN teacher log-prob and est. GFLOPs
    WHEN combining with λ ≥ 0
    THEN return lp − λ · log1p(gflops).
    """
    if lam < 0.0:
        raise ValueError("flop_aware_score: lam must be >= 0")
    return float(lp) - float(lam) * math.log1p(max(0.0, float(gflops)))


def decide_hearf(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-EARF vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and est_gflops < EARLY; else KILL.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_gflops"]) < float(tip["mean_gflops"])):
        return "KILL (no FLOP win vs H-EARLY)"
    return "PROMOTE (FLOP-aware early vs H-EARLY)"
