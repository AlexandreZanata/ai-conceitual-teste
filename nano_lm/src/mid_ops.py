"""H-MID: mid min_new codebook {4,8} + n=1; FLOP dual gate vs EARLY."""

from __future__ import annotations

import random
from typing import Any, Mapping

from earf_ops import flop_aware_score
from lat_ops import EPS_LP

__all__ = [
    "MID_MIN_NEWS",
    "PATIENCES",
    "MidGene",
    "clamp_mid_gene",
    "random_mid_gene",
    "mutate_mid_gene",
    "seed_mid_from_tip",
    "decide_hmid",
    "flop_aware_score",
    "EPS_LP",
]

MidGene = dict[str, Any]
MID_MIN_NEWS = (4, 8)
PATIENCES = (1, 2, 3)


def clamp_mid_gene(gene: MidGene) -> MidGene:
    """
    GIVEN raw early-exit knobs
    WHEN clamping for H-MID
    THEN min_new on {4,8}; n=1; conf/temp/top_p bounded.
    """
    mn = int(round(float(gene["min_new"])))
    min_new = min(MID_MIN_NEWS, key=lambda x: abs(x - mn))
    pat = int(round(float(gene["patience"])))
    patience = min(PATIENCES, key=lambda x: abs(x - pat))
    conf = float(min(0.99, max(0.5, float(gene["conf_threshold"]))))
    temp = float(min(1.5, max(0.2, float(gene["temperature"]))))
    top_p = float(min(1.0, max(0.5, float(gene["top_p"]))))
    return {
        "min_new": int(min_new),
        "patience": int(patience),
        "conf_threshold": conf,
        "n": 1,
        "temperature": temp,
        "top_p": top_p,
    }


def random_mid_gene(rng: random.Random) -> MidGene:
    return clamp_mid_gene(
        {
            "min_new": rng.choice(MID_MIN_NEWS),
            "patience": rng.choice(PATIENCES),
            "conf_threshold": rng.uniform(0.55, 0.95),
            "n": 1,
            "temperature": rng.uniform(0.2, 1.5),
            "top_p": rng.uniform(0.5, 1.0),
        }
    )


def seed_mid_from_tip(tip: MidGene, rng: random.Random) -> MidGene:
    """
    GIVEN an EARLY tip gene
    WHEN warm-starting H-MID
    THEN clamp into MID space (optionally light noise).
    """
    g = dict(tip)
    if rng.random() < 0.5:
        g["conf_threshold"] = float(g["conf_threshold"]) + 0.03 * rng.uniform(-1, 1)
        g["temperature"] = float(g["temperature"]) + 0.1 * rng.uniform(-1, 1)
        g["top_p"] = float(g["top_p"]) + 0.05 * rng.uniform(-1, 1)
    return clamp_mid_gene(g)


def mutate_mid_gene(gene: MidGene, rng: random.Random) -> MidGene:
    g = dict(clamp_mid_gene(gene))
    if rng.random() < 0.4:
        i = MID_MIN_NEWS.index(int(g["min_new"]))
        i = max(0, min(len(MID_MIN_NEWS) - 1, i + rng.choice([-1, 0, 1])))
        g["min_new"] = MID_MIN_NEWS[i]
    if rng.random() < 0.4:
        j = PATIENCES.index(int(g["patience"]))
        j = max(0, min(len(PATIENCES) - 1, j + rng.choice([-1, 0, 1])))
        g["patience"] = PATIENCES[j]
    g["conf_threshold"] = float(g["conf_threshold"]) + 0.05 * rng.uniform(-1, 1)
    g["temperature"] = float(g["temperature"]) + 0.15 * rng.uniform(-1, 1)
    g["top_p"] = float(g["top_p"]) + 0.1 * rng.uniform(-1, 1)
    return clamp_mid_gene(g)


def decide_hmid(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-MID vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and est_gflops < EARLY; else KILL.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_gflops"]) < float(tip["mean_gflops"])):
        return "KILL (no FLOP win vs H-EARLY)"
    return "PROMOTE (mid exit FLOP win vs H-EARLY)"
