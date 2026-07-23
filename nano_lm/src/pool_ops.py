"""H-POOL: warm-start decode pop from other seeds' best genes."""

from __future__ import annotations

import random
from typing import Mapping, Sequence

from decode_genes import Gene, clamp_gene, mutate_gene

__all__ = ["warm_start_pop", "decide_hpool"]


def warm_start_pop(
    pool: Sequence[Gene],
    pop_size: int,
    rng: random.Random,
) -> list[Gene]:
    """
    GIVEN other seeds' best genes and pop_size
    WHEN building an initial population
    THEN return clamped genes: pool copies first, then mutated fills.
    """
    if pop_size < 1:
        raise ValueError("warm_start_pop: pop_size must be >= 1")
    if not pool:
        raise ValueError("warm_start_pop: empty pool")
    genes = [clamp_gene(g) for g in pool]
    out: list[Gene] = [genes[i % len(genes)] for i in range(min(pop_size, len(genes)))]
    while len(out) < pop_size:
        out.append(mutate_gene(genes[len(out) % len(genes)], rng))
    return out


def decide_hpool(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-POOL stats vs cold H-DECKL
    WHEN deciding
    THEN KILL if ≤ cold control; else PROMOTE.
    """
    cold = stats.get("H-DECKL")
    if cold is None:
        return "needs H-DECKL cold control"
    if float(s["mean_lp"]) <= float(cold["mean_lp"]) + 1e-6:
        return "KILL (≤ cold H-DECKL)"
    return "PROMOTE (beats cold H-DECKL)"
