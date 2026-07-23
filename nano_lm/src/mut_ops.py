"""Adaptive mutation scale (1/5 success rule) for H-MUT."""

from __future__ import annotations


def adapt_mutate_scale(
    scale: float,
    success: bool,
    *,
    factor: float = 1.2,
    lo: float = 1e-4,
    hi: float = 0.5,
) -> float:
    """
    GIVEN current mutate scale and whether best fitness improved
    WHEN applying the instantaneous 1/5 success rule
    THEN multiply scale by `factor` on success, divide on failure,
    and clip to [lo, hi].
    """
    if factor <= 1.0:
        raise ValueError("adapt_mutate_scale: factor must be > 1")
    if lo <= 0 or hi < lo:
        raise ValueError("adapt_mutate_scale: invalid bounds")
    if scale <= 0:
        raise ValueError("adapt_mutate_scale: scale must be > 0")
    nxt = scale * factor if success else scale / factor
    return min(hi, max(lo, nxt))


def fitness_improved(prev_best: float, cur_best: float, *, eps: float = 1e-12) -> bool:
    """
    GIVEN previous and current best fitness
    WHEN checking generation success
    THEN True iff cur_best > prev_best + eps.
    """
    return cur_best > prev_best + eps
