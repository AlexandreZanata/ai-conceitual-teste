"""H-TPE: evolve typ_mass gene; dual gate vs H-TYP."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP
from typ_ops import TYP_MASSES

__all__ = [
    "TpeGene",
    "clamp_tpe_gene",
    "random_tpe_gene",
    "mutate_tpe_gene",
    "decide_htpe",
]

TpeGene = dict[str, Any]


def clamp_tpe_gene(gene: TpeGene) -> TpeGene:
    """
    GIVEN raw typical gene
    WHEN clamping
    THEN typ_mass on TYP_MASSES; T in [0.2,1.5]; top_p in [0.5,1].
    """
    raw = float(gene["typ_mass"])
    typ_mass = min(TYP_MASSES, key=lambda x: abs(float(x) - raw))
    temp = float(min(1.5, max(0.2, float(gene["temperature"]))))
    top_p = float(min(1.0, max(0.5, float(gene["top_p"]))))
    return {"typ_mass": float(typ_mass), "temperature": temp, "top_p": top_p}


def random_tpe_gene(rng: random.Random) -> TpeGene:
    return clamp_tpe_gene(
        {
            "typ_mass": rng.choice(list(TYP_MASSES)),
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )


def mutate_tpe_gene(gene: TpeGene, rng: random.Random) -> TpeGene:
    g = dict(clamp_tpe_gene(gene))
    if rng.random() < 0.5:
        i = list(TYP_MASSES).index(float(g["typ_mass"]))
        i = max(0, min(len(TYP_MASSES) - 1, i + rng.choice([-1, 0, 1])))
        g["typ_mass"] = float(TYP_MASSES[i])
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    return clamp_tpe_gene(g)


def decide_htpe(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-TPE vs H-TYP
    WHEN deciding
    THEN PROMOTE only if quality ≥ tip−ε and wall < tip; else KILL.
    """
    tip = stats.get("H-TYP")
    if tip is None:
        return "needs H-TYP control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-TYP)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no speedup vs H-TYP)"
    return "PROMOTE (quality@wall vs H-TYP)"
