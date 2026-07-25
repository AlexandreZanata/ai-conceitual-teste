"""H-GALL: CUDA graph all budgets (never KV) under GRAPH; wall vs H-GRAPH."""

from __future__ import annotations

from typing import Mapping

from graph_ops import GRAPH_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hgall", "GALL_CHUNK", "EPS_LP"]

GALL_CHUNK = GRAPH_CHUNK


def decide_hgall(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-GALL vs H-GRAPH
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and wall < GRAPH; else KILL.
    """
    tip = stats.get("H-GRAPH")
    if tip is None:
        return "needs H-GRAPH control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-GRAPH)"
    if float(s["mean_wall"]) >= float(tip["mean_wall"]):
        return "KILL (no wall win vs H-GRAPH)"
    return "PROMOTE (CUDA graph all budgets under GRAPH)"
