"""H-POOLB: batched multi-prompt POOL decode; throughput gate vs serial."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hpoolb", "EPS_LP"]


def decide_hpoolb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-POOLB vs serial H-POOL
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and tok/s > serial; else KILL.
    """
    tip = stats.get("H-POOL")
    if tip is None:
        return "needs H-POOL control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs serial POOL)"
    if float(s["mean_tps"]) <= float(tip["mean_tps"]):
        return "KILL (no tok/s win vs serial POOL)"
    return "PROMOTE (batched throughput vs serial POOL)"
