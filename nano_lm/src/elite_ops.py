"""Elite-k selection helpers for H-ELI."""

from __future__ import annotations

from typing import Sequence


def select_elite_indices(fits: Sequence[float], elite_k: int) -> list[int]:
    """
    GIVEN fitness scores and elite_k
    WHEN selecting elites
    THEN return the elite_k indices with highest fitness (ties keep lower index).
    """
    if elite_k < 1:
        raise ValueError("elite_k must be >= 1")
    if elite_k > len(fits):
        raise ValueError("elite_k cannot exceed population size")
    ranked = sorted(range(len(fits)), key=lambda i: (-fits[i], i))
    return ranked[:elite_k]


def diversity_collapsed(
    initial: float, final: float, *, min_ratio: float = 0.25, floor: float = 1e-8
) -> bool:
    """
    GIVEN initial and final population diversity
    WHEN checking collapse
    THEN True if final <= floor or final/initial < min_ratio (when initial > floor).
    """
    if final <= floor:
        return True
    if initial <= floor:
        return final <= floor
    return (final / initial) < min_ratio


def fill_plan(pop_size: int, elite_k: int) -> list[str]:
    """
    GIVEN pop_size and elite_k
    WHEN planning next generation slots
    THEN first elite_k slots are 'elite', remaining are 'mutate'.
    """
    if elite_k < 1 or elite_k > pop_size:
        raise ValueError("elite_k must be in [1, pop_size]")
    return ["elite"] * elite_k + ["mutate"] * (pop_size - elite_k)
