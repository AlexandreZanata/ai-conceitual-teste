"""H-GRAPHF: CUDA graph capture under FLAYB decode; wall vs H-FLAYB."""

from __future__ import annotations

from typing import Mapping

from flayb_ops import FLAYB_CHUNK
from lat_ops import EPS_LP

__all__ = ["decide_hgraphf", "GRAPHF_CHUNK", "EPS_LP"]

GRAPHF_CHUNK = FLAYB_CHUNK


def decide_hgraphf(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-GRAPHF vs H-FLAYB
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and wall < FLAYB; else KILL.
    """
    tip = stats.get("H-FLAYB")
    if tip is None:
        return "needs H-FLAYB control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-FLAYB)"
    if float(s["mean_wall"]) >= float(tip["mean_wall"]):
        return "KILL (no wall win vs H-FLAYB)"
    return "PROMOTE (CUDA graph under FLAYB decode)"
