"""H-MPE: evolve min_p gene; dual gate vs H-MINP."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP
from minp_ops import MIN_PS

__all__ = [
    "MpeGene",
    "clamp_mpe_gene",
    "random_mpe_gene",
    "mutate_mpe_gene",
    "decide_hmpe",
]

MpeGene = dict[str, Any]


def clamp_mpe_gene(gene: MpeGene) -> MpeGene:
    """
    GIVEN raw min-p gene
    WHEN clamping
    THEN min_p on MIN_PS; T in [0.2,1.5]; top_p in [0.5,1].
    """
    mp = float(gene["min_p"])
    min_p = min(MIN_PS, key=lambda x: abs(float(x) - mp))
    temp = float(min(1.5, max(0.2, float(gene["temperature"]))))
    top_p = float(min(1.0, max(0.5, float(gene["top_p"]))))
    return {"min_p": float(min_p), "temperature": temp, "top_p": top_p}


def random_mpe_gene(rng: random.Random) -> MpeGene:
    return clamp_mpe_gene(
        {
            "min_p": rng.choice(list(MIN_PS)),
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )


def mutate_mpe_gene(gene: MpeGene, rng: random.Random) -> MpeGene:
    g = dict(clamp_mpe_gene(gene))
    if rng.random() < 0.5:
        i = list(MIN_PS).index(float(g["min_p"]))
        i = max(0, min(len(MIN_PS) - 1, i + rng.choice([-1, 0, 1])))
        g["min_p"] = float(MIN_PS[i])
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    return clamp_mpe_gene(g)


def decide_hmpe(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-MPE vs H-MINP
    WHEN deciding
    THEN PROMOTE only if quality ≥ tip−ε and wall < tip; else KILL.
    """
    tip = stats.get("H-MINP")
    if tip is None:
        return "needs H-MINP control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-MINP)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no speedup vs H-MINP)"
    return "PROMOTE (quality@wall vs H-MINP)"
