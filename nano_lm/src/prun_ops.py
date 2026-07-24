"""H-PRUN: magnitude sparsity gate vs H-STAG (quality@FLOPs)."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "DEFAULT_SPARSITY",
    "scale_flops_by_density",
    "decide_hprun",
    "decide_hprun_formal",
    "EPS_LP",
]

DEFAULT_SPARSITY = 0.3


def scale_flops_by_density(full_flops: float, *, density: float) -> float:
    """
    GIVEN dense FLOP estimate and weight density in (0,1]
    WHEN scaling for magnitude sparsity
    THEN return full_flops · density.
    """
    d = float(density)
    if d <= 0.0:
        return 0.0
    return float(full_flops) * min(1.0, d)


def decide_hprun(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-PRUN vs H-STAG tip (same EARLY decode)
    WHEN deciding (smoke)
    THEN PROMOTE iff lp ≥ STAG−ε and est_gflops < STAG; else KILL.
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-STAG)"
    if not (float(s["mean_gflops"]) < float(tip["mean_gflops"])):
        return "KILL (no FLOP win vs H-STAG)"
    return "PROMOTE (prune+recover vs STAG)"


def decide_hprun_formal(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-PRUN vs H-STAG on formal claim
    WHEN deciding
    THEN PROMOTE iff lp ≥ STAG−ε and wall < STAG
    (density FLOPs alone are not a real dual gate under dense kernels).
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-STAG)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win; density FLOPs alone insufficient)"
    return "PROMOTE (prune+recover wall vs STAG)"
