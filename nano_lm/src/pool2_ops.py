"""H-POOL2: tighter pop×gens + elite-biased warm-start vs H-POOL."""

from __future__ import annotations

import random
from typing import Mapping, Sequence

from decode_genes import Gene, clamp_gene, mutate_gene
from lat_ops import EPS_LP

__all__ = [
    "POOL2_POP",
    "POOL2_GENS",
    "POOL2_POP_FORMAL",
    "POOL2_GENS_FORMAL",
    "warm_start_pop2",
    "decide_hpool2",
]

# Smoke tip H-POOL uses 4×2; formal uses 8×12 — tighten ~2×.
POOL2_POP = 2
POOL2_GENS = 1
POOL2_POP_FORMAL = 4
POOL2_GENS_FORMAL = 6


def warm_start_pop2(
    pool: Sequence[Gene],
    pop_size: int,
    rng: random.Random,
) -> list[Gene]:
    """
    GIVEN other seeds' best genes and pop_size
    WHEN building a tighter warm-start
    THEN prefer exact elite copies; light-mutate only some slots.
    """
    if pop_size < 1:
        raise ValueError("warm_start_pop2: pop_size must be >= 1")
    if not pool:
        raise ValueError("warm_start_pop2: empty pool")
    genes = [clamp_gene(g) for g in pool]
    out: list[Gene] = []
    while len(out) < pop_size:
        base = genes[len(out) % len(genes)]
        if len(out) == 0 or rng.random() >= 0.4:
            out.append(clamp_gene(base))
        else:
            out.append(mutate_gene(base, rng))
    return out


def decide_hpool2(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-POOL2 vs H-POOL tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ POOL−ε and fit teacher_fwd < POOL; else KILL.
    """
    tip = stats.get("H-POOL")
    if tip is None:
        return "needs H-POOL control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-POOL)"
    hyp_fwd = float(s.get("teacher_forwards", tip.get("teacher_forwards", 0)))
    tip_fwd = float(tip.get("teacher_forwards", 0))
    if not (hyp_fwd < tip_fwd):
        return "KILL (no wall save vs H-POOL)"
    return "PROMOTE (tighter POOL holds claim + cheaper fit)"
