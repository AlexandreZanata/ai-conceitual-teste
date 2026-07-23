"""Age-layer helpers for H-AGE (ALPS-lite)."""

from __future__ import annotations

from typing import Sequence


def layer_of_age(age: int, limits: Sequence[int]) -> int:
    """
    GIVEN individual age and ascending layer age limits
    WHEN assigning a layer
    THEN return the first layer whose limit is > age; else last layer.
    """
    if age < 0:
        raise ValueError("layer_of_age: age must be >= 0")
    if not limits:
        raise ValueError("layer_of_age: empty limits")
    for i, lim in enumerate(limits):
        if age < lim:
            return i
    return len(limits) - 1


def bucket_by_layer(
    ages: Sequence[int], limits: Sequence[int]
) -> list[list[int]]:
    """
    GIVEN ages and limits
    WHEN bucketing indices
    THEN return one list of indices per layer (may be empty).
    """
    buckets: list[list[int]] = [[] for _ in range(len(limits))]
    for i, age in enumerate(ages):
        buckets[layer_of_age(age, limits)].append(i)
    return buckets


def child_age(parent_ages: Sequence[int]) -> int:
    """Child age = 1 + max(parent ages); empty parents → 0."""
    if not parent_ages:
        return 0
    return 1 + max(parent_ages)


def default_age_limits(n_layers: int, step: int = 2) -> list[int]:
    """
    GIVEN layer count
    WHEN building ALPS-style limits
    THEN return ascending caps; last cap is a large sentinel.
    """
    if n_layers < 1:
        raise ValueError("default_age_limits: n_layers must be >= 1")
    if step < 1:
        raise ValueError("default_age_limits: step must be >= 1")
    limits = [step * (i + 1) for i in range(n_layers - 1)]
    limits.append(10**9)
    return limits
