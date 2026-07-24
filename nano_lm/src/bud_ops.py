"""H-BUD: co-evolve max_new with EARLY exit gene; vs H-EARLY tip."""

from __future__ import annotations

import random
from typing import Any, Mapping

from early_ops import (
    EarlyGene,
    clamp_early_gene,
    mutate_early_gene,
    random_early_gene,
)
from lat_ops import EPS_LP

__all__ = [
    "BUD_MAX_NEWS",
    "BudGene",
    "clamp_bud_gene",
    "random_bud_gene",
    "mutate_bud_gene",
    "from_early_tip",
    "decide_hbud",
]

BudGene = dict[str, Any]
BUD_MAX_NEWS = (8, 12, 16, 24, 32)


def clamp_bud_gene(gene: BudGene) -> BudGene:
    """
    GIVEN raw bud gene
    WHEN clamping
    THEN early fields via clamp_early_gene; max_new on BUD_MAX_NEWS ≥ min_new.
    """
    base = clamp_early_gene(gene)
    mx = int(round(float(gene.get("max_new", 16))))
    max_new = int(min(BUD_MAX_NEWS, key=lambda x: abs(x - mx)))
    if max_new < int(base["min_new"]):
        ups = [x for x in BUD_MAX_NEWS if x >= int(base["min_new"])]
        max_new = int(ups[0] if ups else BUD_MAX_NEWS[-1])
    base["max_new"] = max_new
    return base


def from_early_tip(gene: EarlyGene, max_new: int = 16) -> BudGene:
    g = dict(clamp_early_gene(gene))
    g["max_new"] = int(max_new)
    return clamp_bud_gene(g)


def random_bud_gene(rng: random.Random) -> BudGene:
    g = random_early_gene(rng)
    g["max_new"] = rng.choice(list(BUD_MAX_NEWS))
    return clamp_bud_gene(g)


def mutate_bud_gene(gene: BudGene, rng: random.Random) -> BudGene:
    g = dict(clamp_bud_gene(gene))
    early = mutate_early_gene(g, rng)
    early["max_new"] = int(g["max_new"])
    if rng.random() < 0.45:
        i = BUD_MAX_NEWS.index(int(g["max_new"]))
        i = max(0, min(len(BUD_MAX_NEWS) - 1, i + rng.choice([-1, 0, 1])))
        early["max_new"] = BUD_MAX_NEWS[i]
    return clamp_bud_gene(early)


def decide_hbud(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-BUD vs H-EARLY
    WHEN deciding
    THEN KILL if dominated on (lp, wall) or quality < EARLY−ε; else PROMOTE.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    tip_dom = float(tip["mean_lp"]) >= float(s["mean_lp"]) - 1e-6 and float(
        tip["mean_wall"]
    ) <= float(s["mean_wall"]) + 1e-6
    strict = float(tip["mean_lp"]) > float(s["mean_lp"]) + 1e-6 or float(
        tip["mean_wall"]
    ) < float(s["mean_wall"]) - 1e-6
    if tip_dom and strict:
        return "KILL (dominated by H-EARLY)"
    if float(s["mean_wall"]) < float(tip["mean_wall"]) and float(s["mean_lp"]) >= float(
        tip["mean_lp"]
    ) - EPS_LP:
        return "PROMOTE (budget gene vs H-EARLY)"
    return "KILL (dominated by H-EARLY)"
