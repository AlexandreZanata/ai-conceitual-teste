"""H-LAT2: stronger latency penalty (λ≥0.4) + n≤2 gene clamp."""

from __future__ import annotations

import random
from typing import Mapping

from decode_genes import Gene, clamp_gene, mutate_gene, random_gene
from lat_ops import decide_hlat

__all__ = [
    "MIN_LAM",
    "MAX_N",
    "clamp_gene_lat2",
    "random_gene_lat2",
    "mutate_gene_lat2",
    "decide_hlat2",
]

MIN_LAM = 0.4
MAX_N = 2


def clamp_gene_lat2(gene: Gene) -> Gene:
    """
    GIVEN a decode gene
    WHEN clamping for H-LAT2
    THEN n ∈ [1, MAX_N] and other fields in BOUNDS.
    """
    g = clamp_gene(gene)
    g["n"] = int(min(MAX_N, max(1, int(g["n"]))))
    return g


def random_gene_lat2(rng: random.Random) -> Gene:
    return clamp_gene_lat2(random_gene(rng))


def mutate_gene_lat2(gene: Gene, rng: random.Random, *, scale: float = 0.15) -> Gene:
    return clamp_gene_lat2(mutate_gene(gene, rng, scale=scale))


def decide_hlat2(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-LAT2 vs B4
    WHEN deciding
    THEN same dual gate as H-LAT (quality ≥ B4−ε and wall < B4).
    """
    return decide_hlat(s, stats)
