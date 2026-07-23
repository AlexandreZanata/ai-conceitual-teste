"""H-DECM: mixture of decode genes; claim picks completion by proxy."""

from __future__ import annotations

from typing import Mapping

from decp_ops import best_index

__all__ = ["MIX_M", "best_index", "decide_hdecm"]

MIX_M = 3


def decide_hdecm(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DECM vs B4 and H-LAT2
    WHEN deciding
    THEN PROMOTE only if lp > B4 and lp > H-LAT2; else KILL.
    """
    b4 = stats.get("B4")
    lat2 = stats.get("H-LAT2")
    if b4 is None:
        return "needs B4 control"
    if lat2 is None:
        return "needs H-LAT2 control"
    s_lp = float(s["mean_lp"])
    if s_lp <= float(b4["mean_lp"]):
        return "KILL (≤ B4)"
    if s_lp <= float(lat2["mean_lp"]):
        return "KILL (≤ H-LAT2)"
    return "PROMOTE (mixture > H-LAT2 and B4)"
