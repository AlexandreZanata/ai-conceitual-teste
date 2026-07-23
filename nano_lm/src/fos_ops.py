"""Fossil-vault helpers for H-FOS: archive + periodic resurrection."""

from __future__ import annotations

from typing import Any, Sequence


def should_resurrect(gen: int, every_k: int) -> bool:
    """
    GIVEN 0-based generation and interval K
    WHEN checking resurrection
    THEN True iff K >= 1 and (gen + 1) is a multiple of K.
    """
    if every_k < 1:
        raise ValueError("should_resurrect: every_k must be >= 1")
    return (gen + 1) % every_k == 0


def vault_push(
    vault: list[dict[str, Any]],
    state: dict[str, Any],
    fit: float,
    *,
    max_size: int,
) -> None:
    """
    GIVEN a fossil vault
    WHEN pushing an extinct lineage
    THEN append {state, fit}; if over max_size, drop the oldest entry.
    """
    if max_size < 1:
        raise ValueError("vault_push: max_size must be >= 1")
    vault.append({"state": state, "fit": fit})
    while len(vault) > max_size:
        vault.pop(0)


def vault_pop(vault: list[dict[str, Any]]) -> dict[str, Any]:
    """
    GIVEN a non-empty vault
    WHEN resurrecting
    THEN remove and return the oldest fossil entry.
    """
    if not vault:
        raise ValueError("vault_pop: empty vault")
    return vault.pop(0)


def worst_index(fits: Sequence[float]) -> int:
    """Index with lowest fitness (ties: higher index is worse)."""
    if not fits:
        raise ValueError("worst_index: empty")
    return min(range(len(fits)), key=lambda i: (fits[i], -i))
