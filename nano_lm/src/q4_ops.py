"""H-Q4: CUDA weight-only int4 (aten int4pack) on DEPTH/PRUN decode."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "DEFAULT_GROUP",
    "DEFAULT_TILES",
    "EPS_LP",
    "decide_hq4",
]

DEFAULT_GROUP = 32
DEFAULT_TILES = 2


def decide_hq4(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-Q4 vs H-DEPTH control (same ckpt, EARLY decode)
    WHEN deciding
    THEN PROMOTE iff lp ≥ DEPTH−ε and wall < DEPTH; else KILL.
    """
    tip = stats.get("H-DEPTH")
    if tip is None:
        return "needs H-DEPTH control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-DEPTH)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-DEPTH)"
    return "PROMOTE (int4 CUDA decode vs DEPTH)"
