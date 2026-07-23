"""Underdog-lottery helpers for H-LOTU: worst gets one free elite clone."""

from __future__ import annotations

from typing import Sequence


def best_index(fits: Sequence[float]) -> int:
    """Index with highest fitness (ties keep lower index)."""
    if not fits:
        raise ValueError("best_index: empty")
    return max(range(len(fits)), key=lambda i: (fits[i], -i))


def worst_index(fits: Sequence[float]) -> int:
    """Index with lowest fitness (ties: higher index is worse)."""
    if not fits:
        raise ValueError("worst_index: empty")
    return min(range(len(fits)), key=lambda i: (fits[i], -i))


def underdog_gift(fits: Sequence[float]) -> tuple[int, int]:
    """
    GIVEN fitness scores
    WHEN awarding the underdog lottery
    THEN return (underdog_index, elite_index).
    If all equal, underdog is a distinct slot when pop >= 2.
    """
    n = len(fits)
    if n < 2:
        raise ValueError("underdog_gift: need pop_size >= 2")
    elite = best_index(fits)
    under = worst_index(fits)
    if under == elite:
        under = (elite + 1) % n
    return under, elite
