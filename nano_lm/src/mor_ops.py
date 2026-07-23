"""Soft mortality helpers for H-MOR."""

from __future__ import annotations

from typing import Sequence


def mortality_k(pop_size: int, *, fraction: float = 0.25) -> int:
    """
    GIVEN population size
    WHEN computing soft-mortality cull count
    THEN return max(1, floor(pop_size * fraction)) but never ≥ pop_size.
    """
    if pop_size < 2:
        raise ValueError("mortality_k: pop_size must be >= 2")
    if not 0.0 < fraction < 1.0:
        raise ValueError("mortality_k: fraction must be in (0, 1)")
    k = max(1, int(pop_size * fraction))
    return min(k, pop_size - 1)


def cull_worst(
    fits: Sequence[float], k: int
) -> tuple[list[int], list[int]]:
    """
    GIVEN fitness scores and cull count k
    WHEN applying soft mortality
    THEN return (survivor_indices, culled_indices) with worst-k culled
    (ties keep lower index among the worst).
    """
    if k < 1:
        raise ValueError("cull_worst: k must be >= 1")
    if k >= len(fits):
        raise ValueError("cull_worst: k must be < population size")
    # Worst first: ascending fitness, then higher index (so lower index survives ties).
    worst_first = sorted(range(len(fits)), key=lambda i: (fits[i], -i))
    culled = worst_first[:k]
    survivors = sorted(worst_first[k:])
    return survivors, culled
