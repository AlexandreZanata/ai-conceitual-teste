"""Tournament parent selection helpers for H-TOU."""

from __future__ import annotations

import random
from typing import Sequence


def tournament_pick(
    fits: Sequence[float], k: int, rng: random.Random
) -> int:
    """
    GIVEN fitness scores and tournament size k
    WHEN picking one parent
    THEN return the index of the highest-fitness candidate among k draws
    (with replacement); ties keep the first-seen winner.
    """
    if not fits:
        raise ValueError("tournament_pick: empty population")
    if k < 1:
        raise ValueError("tournament_pick: k must be >= 1")
    n = len(fits)
    best = rng.randrange(n)
    for _ in range(1, k):
        cand = rng.randrange(n)
        if fits[cand] > fits[best]:
            best = cand
    return best


def select_parents_tournament(
    fits: Sequence[float], count: int, k: int, rng: random.Random
) -> list[int]:
    """
    GIVEN fitness scores, parent count, and k
    WHEN selecting parents for the next generation
    THEN return `count` indices each chosen by tournament_pick.
    """
    if count < 1:
        raise ValueError("select_parents_tournament: count must be >= 1")
    return [tournament_pick(fits, k, rng) for _ in range(count)]
