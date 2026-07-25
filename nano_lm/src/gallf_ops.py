"""H-GALLF: CUDA graph all budgets (never KV) under GRAPHF; wall vs H-GRAPHF."""

from __future__ import annotations

from typing import Mapping

from graphf_ops import GRAPHF_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hgallf", "GALLF_CHUNK", "EPS_LP"]

GALLF_CHUNK = GRAPHF_CHUNK


def decide_hgallf(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-GALLF vs H-GRAPHF
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and wall < GRAPHF; else KILL.
    """
    tip = stats.get("H-GRAPHF")
    if tip is None:
        return "needs H-GRAPHF control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-GRAPHF)"
    if float(s["mean_wall"]) >= float(tip["mean_wall"]):
        return "KILL (no wall win vs H-GRAPHF)"
    return "PROMOTE (CUDA graph all budgets under GRAPHF)"
