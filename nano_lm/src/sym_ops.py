"""Obligate-pair helpers for H-SYM: both parents must beat mean fitness."""

from __future__ import annotations

from typing import Sequence


def mean_fitness(fits: Sequence[float]) -> float:
    """Population mean fitness."""
    if not fits:
        raise ValueError("mean_fitness: empty")
    return sum(fits) / len(fits)


def eligible_above_mean(fits: Sequence[float]) -> list[int]:
    """
    GIVEN fitness scores
    WHEN filtering obligate breeders
    THEN return indices with fitness strictly above the mean.
    """
    m = mean_fitness(fits)
    return [i for i, f in enumerate(fits) if f > m]


def obligate_pairs(eligible: Sequence[int]) -> list[tuple[int, int]]:
    """
    GIVEN eligible indices (already above mean)
    WHEN forming obligate pairs
    THEN pair consecutive (i0,i1), (i2,i3), …; a leftover pairs with i0.
    Empty or singleton → no pairs (sterile).
    """
    n = len(eligible)
    if n < 2:
        return []
    pairs: list[tuple[int, int]] = []
    i = 0
    while i + 1 < n:
        pairs.append((eligible[i], eligible[i + 1]))
        i += 2
    if i < n:
        pairs.append((eligible[i], eligible[0]))
    return pairs
