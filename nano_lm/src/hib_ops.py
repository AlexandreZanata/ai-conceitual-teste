"""Hibernation helpers for H-HIB: skip eval; inherit parent fit × decay."""

from __future__ import annotations


def should_hibernate(gen: int, every_k: int) -> bool:
    """
    GIVEN 0-based generation and interval K
    WHEN checking hibernation
    THEN True iff K >= 1 and (gen + 1) is a multiple of K.
    Gen 0 never hibernates (no parent fits yet).
    """
    if every_k < 1:
        raise ValueError("should_hibernate: every_k must be >= 1")
    if gen < 1:
        return False
    return (gen + 1) % every_k == 0


def decay_fit(parent_fit: float, decay: float) -> float:
    """
    GIVEN parent fitness and decay in (0, 1]
    WHEN inheriting without re-eval
    THEN return parent_fit * decay.
    """
    if not 0.0 < decay <= 1.0:
        raise ValueError("decay_fit: decay must be in (0, 1]")
    return float(parent_fit) * float(decay)


def inherit_fits(parent_fits: list[float], decay: float) -> list[float]:
    """Map each child's parent fitness through decay_fit."""
    return [decay_fit(f, decay) for f in parent_fits]
