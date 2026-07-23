"""Anti-selection helpers for H-ANTI: breed from the worst half."""

from __future__ import annotations

from typing import Sequence


def anti_parent_indices(fits: Sequence[float]) -> list[int]:
    """
    GIVEN fitness scores
    WHEN selecting anti-selection parents
    THEN return indices of the worst max(1, n//2) individuals
    (ties: higher index ranks worse so lower index is preferred as survivor).
    """
    n = len(fits)
    if n < 1:
        raise ValueError("anti_parent_indices: empty population")
    k = max(1, n // 2)
    worst_first = sorted(range(n), key=lambda i: (fits[i], -i))
    return worst_first[:k]
