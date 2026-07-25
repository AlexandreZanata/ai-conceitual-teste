"""H-SROUTE: length-budget ROUTE vs frozen SERVE recipe (full-stack)."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from route_ops import arm_dominates
from serve_ops import SERVE_CHUNK

__all__ = [
    "decide_hsroute",
    "arm_dominates",
    "SROUTE_CHUNK",
    "EPS_LP",
]

SROUTE_CHUNK = SERVE_CHUNK


def decide_hsroute(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-SROUTE (ROUTE stack) vs frozen H-SERVE recipe
    WHEN deciding
    THEN KILL iff SERVE dominates SROUTE on (lp, wall); else PROMOTE.
    """
    serve = stats.get("H-SERVE")
    if serve is None:
        return "needs H-SERVE control"
    if arm_dominates(serve, s, eps_lp=eps_lp):
        return "KILL (dominated by H-SERVE)"
    return "PROMOTE (ROUTE not dominated by SERVE)"
