"""H-CHBAT: CBAT with CHB tip B=256; tok/s gate vs H-CBAT."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hchbat", "CHBAT_CHUNK", "EPS_LP"]

# CHB formal winner B=256 (systems tip deepen under CBAT throughput path).
CHBAT_CHUNK = 256


def decide_hchbat(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-CHBAT vs H-CBAT
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and tok/s > CBAT; else KILL.
    """
    tip = stats.get("H-CBAT")
    if tip is None:
        return "needs H-CBAT control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-CBAT)"
    if float(s["mean_tps"]) <= float(tip["mean_tps"]):
        return "KILL (no tok/s win vs H-CBAT)"
    return "PROMOTE (CHB B under CBAT)"
