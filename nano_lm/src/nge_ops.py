"""H-NGE: evolve no-repeat n-gram gene; dual gate vs H-NGRAM."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP
from ngram_ops import NGRAM_SIZES

__all__ = [
    "NgeGene",
    "clamp_nge_gene",
    "random_nge_gene",
    "mutate_nge_gene",
    "decide_hnge",
]

NgeGene = dict[str, Any]


def clamp_nge_gene(gene: NgeGene) -> NgeGene:
    """
    GIVEN raw ngram gene
    WHEN clamping
    THEN ngram_size on NGRAM_SIZES; T in [0.2,1.5]; top_p in [0.5,1].
    """
    n = int(round(float(gene["ngram_size"])))
    size = min(NGRAM_SIZES, key=lambda x: abs(int(x) - n))
    temp = float(min(1.5, max(0.2, float(gene["temperature"]))))
    top_p = float(min(1.0, max(0.5, float(gene["top_p"]))))
    return {"ngram_size": int(size), "temperature": temp, "top_p": top_p}


def random_nge_gene(rng: random.Random) -> NgeGene:
    return clamp_nge_gene(
        {
            "ngram_size": rng.choice(list(NGRAM_SIZES)),
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )


def mutate_nge_gene(gene: NgeGene, rng: random.Random) -> NgeGene:
    g = dict(clamp_nge_gene(gene))
    if rng.random() < 0.5:
        i = list(NGRAM_SIZES).index(int(g["ngram_size"]))
        i = max(0, min(len(NGRAM_SIZES) - 1, i + rng.choice([-1, 0, 1])))
        g["ngram_size"] = int(NGRAM_SIZES[i])
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    return clamp_nge_gene(g)


def decide_hnge(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-NGE vs H-NGRAM
    WHEN deciding
    THEN PROMOTE only if quality ≥ tip−ε and wall < tip; else KILL.
    """
    tip = stats.get("H-NGRAM")
    if tip is None:
        return "needs H-NGRAM control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-NGRAM)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no speedup vs H-NGRAM)"
    return "PROMOTE (quality@wall vs H-NGRAM)"
