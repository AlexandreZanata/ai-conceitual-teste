"""H-POOLF: FLOP dual gate vs H-POOL; gene clamp n≤2."""

from __future__ import annotations

import random
from typing import Mapping

from decode_genes import Gene, clamp_gene, mutate_gene, random_gene
from earf_ops import flop_aware_score
from lat_ops import EPS_LP

__all__ = [
    "N_MAX",
    "clamp_poolf_gene",
    "random_poolf_gene",
    "mutate_poolf_gene",
    "seed_poolf_from_tip",
    "decide_hpoolf",
    "flop_aware_score",
    "EPS_LP",
]

N_MAX = 2


def clamp_poolf_gene(gene: Gene) -> Gene:
    """
    GIVEN a decode gene
    WHEN clamping for H-POOLF
    THEN standard bounds and n ≤ N_MAX.
    """
    g = clamp_gene(gene)
    g["n"] = int(min(N_MAX, max(1, int(g["n"]))))
    return g


def random_poolf_gene(rng: random.Random) -> Gene:
    return clamp_poolf_gene(random_gene(rng))


def mutate_poolf_gene(gene: Gene, rng: random.Random) -> Gene:
    return clamp_poolf_gene(mutate_gene(gene, rng))


def seed_poolf_from_tip(tip: Gene, rng: random.Random) -> Gene:
    """
    GIVEN POOL tip gene
    WHEN warm-starting
    THEN clamp into n≤2 space (optional light noise).
    """
    g = dict(tip)
    if rng.random() < 0.5:
        g["temperature"] = float(g["temperature"]) + 0.05 * rng.uniform(-1, 1)
        g["top_p"] = float(g["top_p"]) + 0.05 * rng.uniform(-1, 1)
    return clamp_poolf_gene(g)


def decide_hpoolf(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-POOLF vs H-POOL tip
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
    return "PROMOTE (FLOP-aware POOL vs tip)"
