"""Linear rank selection helpers for H-RAN."""

from __future__ import annotations

import random
from typing import Sequence


def linear_rank_weights(fits: Sequence[float]) -> list[float]:
    """
    GIVEN fitness scores
    WHEN assigning linear ranks
    THEN worst gets weight 1.0 and best gets weight n (ties keep lower index worse).
    """
    if not fits:
        raise ValueError("linear_rank_weights: empty population")
    order = sorted(range(len(fits)), key=lambda i: (fits[i], i))
    weights = [0.0] * len(fits)
    for rank, idx in enumerate(order, start=1):
        weights[idx] = float(rank)
    return weights


def linear_ranks(fits: Sequence[float]) -> list[int]:
    """Return integer ranks (1=worst … n=best) aligned to fitness indices."""
    return [int(w) for w in linear_rank_weights(fits)]


def select_parents_rank(
    fits: Sequence[float], count: int, rng: random.Random
) -> list[int]:
    """
    GIVEN fitness scores and parent count
    WHEN selecting parents by linear-rank roulette
    THEN return `count` indices with probability proportional to rank weight.
    """
    if count < 1:
        raise ValueError("select_parents_rank: count must be >= 1")
    weights = linear_rank_weights(fits)
    total = sum(weights)
    parents: list[int] = []
    for _ in range(count):
        r = rng.random() * total
        acc = 0.0
        chosen = len(weights) - 1
        for i, w in enumerate(weights):
            acc += w
            if r <= acc:
                chosen = i
                break
        parents.append(chosen)
    return parents
