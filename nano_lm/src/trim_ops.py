"""H-TRIM: freeze tip n; FLOP dual gate vs H-POOL."""

from __future__ import annotations

import random
from typing import Mapping

from decode_genes import Gene, clamp_gene, mutate_gene
from earf_ops import flop_aware_score
from lat_ops import EPS_LP

__all__ = [
    "clamp_trim_gene",
    "mutate_trim_gene",
    "seed_trim_from_tip",
    "decide_htrim",
    "flop_aware_score",
    "EPS_LP",
]


def clamp_trim_gene(gene: Gene, frozen_n: int) -> Gene:
    """
    GIVEN a decode gene and frozen tip n
    WHEN clamping for H-TRIM
    THEN standard bounds with n forced to frozen_n.
    """
    g = clamp_gene(gene)
    g["n"] = int(max(1, int(frozen_n)))
    return g


def mutate_trim_gene(gene: Gene, frozen_n: int, rng: random.Random) -> Gene:
    """
    GIVEN a gene
    WHEN mutating under H-TRIM
    THEN other knobs may change; n stays frozen_n.
    """
    return clamp_trim_gene(mutate_gene(gene, rng), frozen_n)


def seed_trim_from_tip(tip: Gene, rng: random.Random) -> Gene:
    """
    GIVEN POOL tip
    WHEN warm-starting TRIM
    THEN keep tip n; optional light noise on continuous knobs.
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
    return clamp_trim_gene(g, frozen_n)


def decide_htrim(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-TRIM vs H-POOL tip
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
    return "PROMOTE (TRIM frozen-n FLOP vs tip)"
