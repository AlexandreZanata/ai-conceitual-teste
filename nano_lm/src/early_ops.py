"""H-EARLY: evolve early-exit / adaptive-length knobs; dual gate vs B4."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP

__all__ = [
    "MIN_NEWS",
    "PATIENCES",
    "EarlyGene",
    "clamp_early_gene",
    "random_early_gene",
    "mutate_early_gene",
    "decide_hearly",
    "should_early_exit",
]

EarlyGene = dict[str, Any]
MIN_NEWS = (4, 8, 12)
PATIENCES = (1, 2, 3)


def should_early_exit(
    *,
    n_new: int,
    min_new: int,
    streak: int,
    patience: int,
) -> bool:
    """
    GIVEN generation progress and confidence streak
    WHEN checking early exit
    THEN true iff n_new ≥ min_new and streak ≥ patience.
    """
    return int(n_new) >= int(min_new) and int(streak) >= int(patience)


def clamp_early_gene(gene: EarlyGene) -> EarlyGene:
    """
    GIVEN raw early-exit knobs
    WHEN clamping
    THEN min_new/patience on codebooks; conf in [0.5, 0.99]; n in [1, 2].
    """
    mn = int(round(float(gene["min_new"])))
    min_new = min(MIN_NEWS, key=lambda x: abs(x - mn))
    pat = int(round(float(gene["patience"])))
    patience = min(PATIENCES, key=lambda x: abs(x - pat))
    conf = float(min(0.99, max(0.5, float(gene["conf_threshold"]))))
    n = int(min(2, max(1, round(float(gene.get("n", 1))))))
    temp = float(min(1.5, max(0.2, float(gene["temperature"]))))
    top_p = float(min(1.0, max(0.5, float(gene["top_p"]))))
    return {
        "min_new": int(min_new),
        "patience": int(patience),
        "conf_threshold": conf,
        "n": n,
        "temperature": temp,
        "top_p": top_p,
    }


def random_early_gene(rng: random.Random) -> EarlyGene:
    return clamp_early_gene(
        {
            "min_new": rng.choice(MIN_NEWS),
            "patience": rng.choice(PATIENCES),
            "conf_threshold": rng.uniform(0.55, 0.95),
            "n": rng.choice([1, 2]),
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )


def mutate_early_gene(gene: EarlyGene, rng: random.Random) -> EarlyGene:
    g = dict(clamp_early_gene(gene))
    if rng.random() < 0.4:
        i = MIN_NEWS.index(int(g["min_new"]))
        i = max(0, min(len(MIN_NEWS) - 1, i + rng.choice([-1, 0, 1])))
        g["min_new"] = MIN_NEWS[i]
    if rng.random() < 0.4:
        j = PATIENCES.index(int(g["patience"]))
        j = max(0, min(len(PATIENCES) - 1, j + rng.choice([-1, 0, 1])))
        g["patience"] = PATIENCES[j]
    g["conf_threshold"] = float(g["conf_threshold"]) + 0.05 * rng.uniform(-1, 1)
    g["n"] = int(g["n"]) + rng.choice([-1, 0, 1])
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    return clamp_early_gene(g)


def decide_hearly(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-EARLY vs B4
    WHEN deciding
    THEN PROMOTE only if quality ≥ B4−ε and wall < B4; else KILL.
    """
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if float(s["mean_lp"]) < float(b4["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs B4)"
    if not (float(s["mean_wall"]) < float(b4["mean_wall"])):
        return "KILL (no speedup vs B4)"
    return "PROMOTE (quality@wall vs B4)"
