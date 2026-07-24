"""H-PROX: CE-only fit proxy for POOL search; teacher claim unchanged."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["EPS_LP", "decide_hprox"]


def decide_hprox(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-PROX vs H-POOL claim teacher_lp
    WHEN deciding
    THEN PROMOTE iff claim lp ≥ POOL−ε; else KILL.
    """
    tip = stats.get("H-POOL")
    if tip is None:
        return "needs H-POOL control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (claim quality drop vs H-POOL)"
    return "PROMOTE (CE proxy fit holds claim vs H-POOL)"
