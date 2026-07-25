"""H-CBAT: chunked KV prefill under batched EARLY; tok/s gate vs H-BAT."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hcbat", "EPS_LP"]


def decide_hcbat(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-CBAT vs H-BAT
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and tok/s > BAT; else KILL.
    """
    tip = stats.get("H-BAT")
    if tip is None:
        return "needs H-BAT control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-BAT)"
    if float(s["mean_tps"]) <= float(tip["mean_tps"]):
        return "KILL (no tok/s win vs H-BAT)"
    return "PROMOTE (chunked prefill under BAT)"
