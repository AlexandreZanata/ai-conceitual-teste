"""Island speciation helpers for H-SPE."""

from __future__ import annotations

from typing import Sequence


def split_islands(pop_size: int, n_islands: int) -> list[list[int]]:
    """
    GIVEN pop_size and island count
    WHEN partitioning indices
    THEN return n contiguous index lists of as-equal size as possible.
    """
    if n_islands < 2:
        raise ValueError("split_islands: n_islands must be >= 2")
    if pop_size < n_islands:
        raise ValueError("split_islands: pop_size must be >= n_islands")
    base, rem = divmod(pop_size, n_islands)
    out: list[list[int]] = []
    start = 0
    for i in range(n_islands):
        size = base + (1 if i < rem else 0)
        out.append(list(range(start, start + size)))
        start += size
    return out


def should_migrate(gen: int, migrate_every: int) -> bool:
    """
    GIVEN 0-based generation index and migrate_every M
    WHEN checking migration
    THEN True iff M > 0 and (gen + 1) is a multiple of M.
    """
    if migrate_every < 1:
        raise ValueError("should_migrate: migrate_every must be >= 1")
    return (gen + 1) % migrate_every == 0


def ring_migrate_pairs(n_islands: int) -> list[tuple[int, int]]:
    """
    GIVEN island count
    WHEN planning top-1 ring migration
    THEN return (src_island, dst_island) pairs for i → (i+1) % n.
    """
    if n_islands < 2:
        raise ValueError("ring_migrate_pairs: n_islands must be >= 2")
    return [(i, (i + 1) % n_islands) for i in range(n_islands)]


def worst_in_island(fits: Sequence[float], indices: Sequence[int]) -> int:
    """Return the index in `indices` with lowest fitness."""
    if not indices:
        raise ValueError("worst_in_island: empty island")
    return min(indices, key=lambda i: fits[i])


def best_in_island(fits: Sequence[float], indices: Sequence[int]) -> int:
    """Return the index in `indices` with highest fitness."""
    if not indices:
        raise ValueError("best_in_island: empty island")
    return max(indices, key=lambda i: fits[i])
