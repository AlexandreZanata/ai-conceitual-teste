"""Catastrophe helpers for H-CAT: keep top-1, refill with immigrants."""

from __future__ import annotations

from typing import Sequence


def should_catastrophe(gen: int, every_k: int) -> bool:
    """
    GIVEN 0-based generation and interval K
    WHEN checking catastrophe
    THEN True iff K >= 1 and (gen + 1) is a multiple of K.
    """
    if every_k < 1:
        raise ValueError("should_catastrophe: every_k must be >= 1")
    return (gen + 1) % every_k == 0


def elite_index(fits: Sequence[float]) -> int:
    """Index with highest fitness (ties keep lower index)."""
    if not fits:
        raise ValueError("elite_index: empty")
    return max(range(len(fits)), key=lambda i: (fits[i], -i))


def immigrant_count(pop_size: int, *, keep: int = 1) -> int:
    """
    GIVEN population size and elite keep count
    WHEN planning a catastrophe refill
    THEN return how many random immigrants are needed.
    """
    if pop_size < 1:
        raise ValueError("immigrant_count: pop_size must be >= 1")
    if keep < 1 or keep > pop_size:
        raise ValueError("immigrant_count: keep must be in [1, pop_size]")
    return pop_size - keep
