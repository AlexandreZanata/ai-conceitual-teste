"""H-CPOOLB: chunked KV prefill under batched POOL; tok/s gate vs H-POOLB."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hcpoolb", "CPOOLB_CHUNK", "EPS_LP"]

# CHB formal winner B=256 (systems tip deepen under batch quality path).
CPOOLB_CHUNK = 256


def decide_hcpoolb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-CPOOLB vs H-POOLB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and tok/s > POOLB; else KILL.
    """
    tip = stats.get("H-POOLB")
    if tip is None:
        return "needs H-POOLB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-POOLB)"
    if float(s["mean_tps"]) <= float(tip["mean_tps"]):
        return "KILL (no tok/s win vs H-POOLB)"
    return "PROMOTE (chunked prefill under POOLB)"
