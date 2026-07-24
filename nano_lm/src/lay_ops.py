"""H-LAY: layer early-exit knobs; dual gate vs H-EARLY (wall or GFLOPs)."""

from __future__ import annotations

import math
import random
from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "MAX_SKIPS",
    "LayGene",
    "clamp_lay_gene",
    "random_lay_gene",
    "mutate_lay_gene",
    "flop_aware_score",
    "scale_flops_by_layers",
    "decide_hlay",
    "EPS_LP",
]

LayGene = dict[str, float | int]
MAX_SKIPS = (0, 1)


def flop_aware_score(lp: float, gflops: float, lam: float) -> float:
    """
    GIVEN teacher lp and est GFLOPs
    WHEN scoring for search
    THEN return lp − λ · log1p(GFLOPs).
    """
    if lam < 0.0:
        raise ValueError("flop_aware_score: lam must be >= 0")
    return float(lp) - float(lam) * math.log1p(max(0.0, float(gflops)))


def scale_flops_by_layers(
    full_flops: float,
    *,
    layer_evals: int,
    token_evals: int,
    n_layers: int,
) -> float:
    """
    GIVEN full-model FLOP estimate and layer counters
    WHEN scaling for partial depth
    THEN multiply by layer_evals / (token_evals · n_layers).
    """
    denom = int(token_evals) * int(n_layers)
    if denom < 1 or int(layer_evals) < 0:
        return float(full_flops)
    return float(full_flops) * (float(layer_evals) / float(denom))


def clamp_lay_gene(gene: Mapping[str, float | int]) -> LayGene:
    """
    GIVEN raw layer-exit knobs
    WHEN clamping
    THEN max_skip ∈ {0,1}; lay_conf ∈ [0.5, 0.99].
    """
    raw = int(round(float(gene["max_skip"])))
    max_skip = min(MAX_SKIPS, key=lambda x: abs(x - raw))
    conf = float(min(0.99, max(0.5, float(gene["lay_conf"]))))
    return {"max_skip": int(max_skip), "lay_conf": conf}


def random_lay_gene(rng: random.Random) -> LayGene:
    return clamp_lay_gene(
        {"max_skip": rng.choice(MAX_SKIPS), "lay_conf": rng.uniform(0.55, 0.95)}
    )


def mutate_lay_gene(gene: LayGene, rng: random.Random) -> LayGene:
    g = dict(clamp_lay_gene(gene))
    if rng.random() < 0.5:
        g["max_skip"] = int(g["max_skip"]) + rng.choice([-1, 0, 1])
    g["lay_conf"] = float(g["lay_conf"]) + 0.05 * rng.uniform(-1, 1)
    return clamp_lay_gene(g)


def decide_hlay(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-LAY vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and (wall < EARLY or gflops < EARLY).
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    flop_win = float(s["mean_gflops"]) < float(tip["mean_gflops"])
    if not (wall_win or flop_win):
        return "KILL (no wall/GFLOPs win vs H-EARLY)"
    return "PROMOTE (layer-exit vs EARLY)"
