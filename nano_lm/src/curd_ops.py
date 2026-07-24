"""H-CURD: difficulty (teacher-NLL) curriculum; xor length stages."""

from __future__ import annotations

from typing import Mapping

from cur_ops import N_STAGES

__all__ = [
    "N_STAGES",
    "curd_stage",
    "easy_frac",
    "decide_hcurd",
]


def curd_stage(step: int, steps: int, *, n_stages: int = N_STAGES) -> int:
    """
    GIVEN step in [0, steps) and n_stages ≥ 1
    WHEN picking difficulty stage
    THEN return stage index in [0, n_stages).
    """
    n = int(n_stages)
    if n < 1:
        raise ValueError("curd_stage: n_stages must be >= 1")
    if steps <= 1:
        return n - 1
    t = max(0, min(int(step), int(steps) - 1))
    return min(n - 1, (t * n) // int(steps))


def easy_frac(stage: int, *, n_stages: int = N_STAGES) -> float:
    """
    GIVEN stage index
    WHEN selecting easiest examples
    THEN return fraction (stage+1)/n_stages in (0, 1].
    """
    n = int(n_stages)
    s = max(0, min(int(stage), n - 1))
    return float(s + 1) / float(n)


def decide_hcurd(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-CURD vs H-CURL2 tip @ equal steps
    WHEN deciding
    THEN PROMOTE iff teacher_lp > tip; else KILL.
    """
    tip = stats.get("H-CURL2")
    if tip is None:
        return "needs H-CURL2 control"
    if float(s["mean_lp"]) > float(tip["mean_lp"]) + 1e-6:
        return "PROMOTE (beats H-CURL2 tip)"
    return "KILL (≤ H-CURL2 tip)"
