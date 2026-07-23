"""H-DECQ: quantized discrete decode gene codes (+ LAT2 n≤2)."""

from __future__ import annotations

import random
from typing import Mapping, Sequence

from decode_genes import Gene, mutate_gene, random_gene
from lat2_ops import clamp_gene_lat2

__all__ = [
    "TEMP_LEVELS",
    "TOP_P_LEVELS",
    "quantize_gene",
    "random_gene_decq",
    "mutate_gene_decq",
    "decide_hdecq",
]

TEMP_LEVELS = (0.4, 0.7, 1.0, 1.3)
TOP_P_LEVELS = (0.55, 0.75, 0.95)


def _nearest(levels: Sequence[float], value: float) -> float:
    return float(min(levels, key=lambda x: abs(float(x) - float(value))))


def quantize_gene(gene: Gene) -> Gene:
    """
    GIVEN a decode gene
    WHEN quantizing
    THEN snap temperature/top_p to codebook and clamp n≤2.
    """
    g = clamp_gene_lat2(gene)
    g["temperature"] = _nearest(TEMP_LEVELS, float(g["temperature"]))
    g["top_p"] = _nearest(TOP_P_LEVELS, float(g["top_p"]))
    return g


def random_gene_decq(rng: random.Random) -> Gene:
    g = random_gene(rng)
    g["temperature"] = rng.choice(TEMP_LEVELS)
    g["top_p"] = rng.choice(TOP_P_LEVELS)
    return quantize_gene(g)


def mutate_gene_decq(gene: Gene, rng: random.Random, *, scale: float = 0.15) -> Gene:
    """Mutate via continuous nudge then re-quantize (discrete codes)."""
    return quantize_gene(mutate_gene(gene, rng, scale=scale))


def decide_hdecq(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DECQ vs B4 and H-DECM
    WHEN deciding
    THEN PROMOTE only if lp > B4 and lp > H-DECM; else KILL.
    """
    b4 = stats.get("B4")
    decm = stats.get("H-DECM")
    if b4 is None:
        return "needs B4 control"
    if decm is None:
        return "needs H-DECM control"
    s_lp = float(s["mean_lp"])
    if s_lp <= float(b4["mean_lp"]):
        return "KILL (≤ B4)"
    if s_lp <= float(decm["mean_lp"]):
        return "KILL (≤ H-DECM)"
    return "PROMOTE (quantized mixture > H-DECM and B4)"
