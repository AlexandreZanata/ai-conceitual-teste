"""H-HOR: freeze tip n; clamp horizon≤2; FLOP dual gate vs H-POOL."""

from __future__ import annotations

import random
from typing import Mapping

from decode_genes import Gene, clamp_gene, mutate_gene
from earf_ops import flop_aware_score
from lat_ops import EPS_LP

__all__ = [
    "HORIZON_MAX",
    "clamp_hor_gene",
    "mutate_hor_gene",
    "seed_hor_from_tip",
    "decide_hhor",
    "flop_aware_score",
    "EPS_LP",
]

HORIZON_MAX = 2


def clamp_hor_gene(gene: Gene, frozen_n: int) -> Gene:
    """
    GIVEN a decode gene and frozen tip n
    WHEN clamping for H-HOR
    THEN n = frozen_n and horizon ≤ HORIZON_MAX.
    """
    g = clamp_gene(gene)
    g["n"] = int(max(1, int(frozen_n)))
    g["horizon"] = int(min(HORIZON_MAX, max(1, int(g["horizon"]))))
    return g


def mutate_hor_gene(gene: Gene, frozen_n: int, rng: random.Random) -> Gene:
    """
    GIVEN a gene
    WHEN mutating under H-HOR
    THEN other knobs may change; n frozen; horizon ≤ HORIZON_MAX.
    """
    return clamp_hor_gene(mutate_gene(gene, rng), frozen_n)


def seed_hor_from_tip(tip: Gene, rng: random.Random) -> Gene:
    """
    GIVEN POOL tip
    WHEN warm-starting HOR
    THEN keep tip n; clamp horizon; optional light noise.
    """
    frozen_n = int(tip["n"])
    g = dict(tip)
    if rng.random() < 0.5:
        g["temperature"] = float(g["temperature"]) + 0.05 * rng.uniform(-1, 1)
        g["top_p"] = float(g["top_p"]) + 0.05 * rng.uniform(-1, 1)
    if rng.random() < 0.35:
        g["k"] = int(g["k"]) + rng.choice([-1, 0, 1])
        g["horizon"] = int(g["horizon"]) + rng.choice([-1, 0, 1])
        g["block"] = int(g["block"]) + rng.choice([-1, 0, 1])
    return clamp_hor_gene(g, frozen_n)


def decide_hhor(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-HOR vs H-POOL tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ POOL−ε and est_gflops < POOL; else KILL.
    """
    tip = stats.get("H-POOL")
    if tip is None:
        return "needs H-POOL control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-POOL)"
    if not (float(s["mean_gflops"]) < float(tip["mean_gflops"])):
        return "KILL (no FLOP win vs H-POOL)"
    return "PROMOTE (HOR frozen-n horizon≤2 FLOP vs tip)"
