"""LR / temperature schedules for KD variants (cosine vs anneal)."""

from __future__ import annotations

import math


def progress(step: int, total: int) -> float:
    """Normalized step in [0, 1]."""
    if total <= 1:
        return 1.0
    return min(1.0, max(0.0, step / (total - 1)))


def cosine_value(start: float, end: float, t: float) -> float:
    """
    GIVEN start/end and t in [0,1]
    WHEN applying cosine decay
    THEN return end + 0.5*(start-end)*(1+cos(pi*t)).
    """
    t = min(1.0, max(0.0, t))
    return end + 0.5 * (start - end) * (1.0 + math.cos(math.pi * t))


def linear_value(start: float, end: float, t: float) -> float:
    """
    GIVEN start/end and t in [0,1]
    WHEN applying linear anneal
    THEN return start + (end-start)*t.
    """
    t = min(1.0, max(0.0, t))
    return start + (end - start) * t


def schedule_pair(
    kind: str,
    step: int,
    total: int,
    *,
    lr_start: float,
    lr_end: float,
    temp_start: float,
    temp_end: float,
) -> tuple[float, float]:
    """
    GIVEN schedule kind and step
    WHEN sampling LR and KD temperature
    THEN cosine decays LR (temp fixed at temp_start);
         anneal linearly decays both LR and temperature.
    """
    t = progress(step, total)
    if kind == "cosine":
        return cosine_value(lr_start, lr_end, t), temp_start
    if kind == "anneal":
        return linear_value(lr_start, lr_end, t), linear_value(
            temp_start, temp_end, t
        )
    raise ValueError(f"unknown schedule kind: {kind}")
