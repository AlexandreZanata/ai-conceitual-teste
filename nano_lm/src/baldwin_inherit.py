"""Baldwin inheritance: reproduce from genotype, never learned phenotype."""

from __future__ import annotations

from typing import Mapping, TypeVar

T = TypeVar("T")


def inherit_weights(
    genotype: T,
    phenotype: T,
    *,
    mode: str = "baldwin",
) -> T:
    """
    GIVEN genotype (birth weights) and phenotype (after lifetime learning)
    WHEN selecting inheritance for the next generation
    THEN baldwin returns genotype; lamarck returns phenotype.
    """
    if mode == "baldwin":
        return genotype
    if mode == "lamarck":
        return phenotype
    raise ValueError(f"unknown inherit mode: {mode}")


def assert_geno_unchanged(
    before: Mapping[str, object], after: Mapping[str, object]
) -> bool:
    """True iff every tensor/object identity-or-equality matches (contract helper)."""
    if before.keys() != after.keys():
        return False
    for k in before:
        a, b = before[k], after[k]
        if hasattr(a, "equal") and hasattr(b, "equal"):
            if not bool(a.equal(b)):  # type: ignore[union-attr]
                return False
        elif a != b:
            return False
    return True
