"""H-CACHE: KV-cached EARLY decode; dual wall vs H-EARLY + B4."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hcache"]


def decide_hcache(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-CACHE vs H-EARLY tip and B4
    WHEN deciding
    THEN PROMOTE iff quality ≥ EARLY−ε and wall < EARLY and B4 dual holds.
    """
    early = stats.get("H-EARLY")
    b4 = stats.get("B4")
    if early is None or b4 is None:
        return "needs H-EARLY+B4 controls"
    if float(s["mean_lp"]) < float(early["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_wall"]) < float(early["mean_wall"])):
        return "KILL (no wall save vs H-EARLY)"
    if float(s["mean_lp"]) < float(b4["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs B4)"
    if not (float(s["mean_wall"]) < float(b4["mean_wall"])):
        return "KILL (no speedup vs B4)"
    return "PROMOTE (KV cache wall vs EARLY+B4)"
