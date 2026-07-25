"""H-DEPTHA: DEPTH student under ADAMF train; ms/step vs H-ADAMF."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hdeptha", "EPS_LP"]


def decide_hdeptha(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-DEPTHA vs H-ADAMF tip (same ADAMF I/O)
    WHEN deciding
    THEN PROMOTE iff lp ≥ ADAMF−ε and ms/step < ADAMF.
    """
    tip = stats.get("H-ADAMF")
    if tip is None:
        return "needs H-ADAMF control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-ADAMF)"
    if not (float(s["mean_ms_step"]) < float(tip["mean_ms_step"])):
        return "KILL (no train step-time win vs H-ADAMF)"
    return "PROMOTE (DEPTH under ADAMF)"
