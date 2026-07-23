"""Season helpers for H-SEA: alternate CE vs teacher_lp fitness by generation."""

from __future__ import annotations


def season_kind(gen: int) -> str:
    """
    GIVEN 0-based generation index
    WHEN choosing the seasonal fitness
    THEN odd gens → \"ce\"; even gens → \"teacher_lp\".
    """
    if gen < 0:
        raise ValueError("season_kind: gen must be >= 0")
    return "ce" if gen % 2 == 1 else "teacher_lp"


def is_ce_season(gen: int) -> bool:
    """True iff this generation uses CE fitness."""
    return season_kind(gen) == "ce"
