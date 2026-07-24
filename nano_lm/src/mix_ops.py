"""H-MIX: protocol stack PRUN ckpt ⊕ LAY decode (not a tip H-ID)."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = ["decide_hmix", "EPS_LP"]


def decide_hmix(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN PRUN⊕LAY mix vs PRUN+EARLY control
    WHEN deciding
    THEN PROTOCOL iff lp ≥ PRUN−ε and wall < PRUN; else KILL.
    Never tip PROMOTE (compose branch closed).
    """
    tip = stats.get("H-PRUN")
    if tip is None:
        return "needs H-PRUN control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-PRUN; do not stack)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-PRUN; stack adds no value)"
    return "PROTOCOL (PRUN ckpt ⊕ LAY; not a tip H-ID)"
