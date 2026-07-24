"""H-ALAT (H-αT): KD α/T schedule under CURL length stages."""

from __future__ import annotations

from typing import Mapping

from curd_ops import curd_stage

__all__ = [
    "curd_stage",
    "alat_alpha",
    "alat_temp",
    "decide_halat",
    "ALPHA_LO",
    "ALPHA_HI",
    "TEMP_HI",
    "TEMP_LO",
]

ALPHA_LO = 0.25
ALPHA_HI = 0.75
TEMP_HI = 3.0
TEMP_LO = 1.0


def _frac(stage: int, n_stages: int) -> float:
    n = int(n_stages)
    if n <= 1:
        return 1.0
    s = max(0, min(int(stage), n - 1))
    return float(s) / float(n - 1)


def alat_alpha(
    stage: int,
    *,
    n_stages: int = 3,
    alpha_lo: float = ALPHA_LO,
    alpha_hi: float = ALPHA_HI,
) -> float:
    """
    GIVEN length-curriculum stage
    WHEN scheduling CE weight α
    THEN ramp alpha_lo → alpha_hi (more CE on longer seq).
    """
    f = _frac(stage, n_stages)
    return float(alpha_lo) + f * (float(alpha_hi) - float(alpha_lo))


def alat_temp(
    stage: int,
    *,
    n_stages: int = 3,
    temp_hi: float = TEMP_HI,
    temp_lo: float = TEMP_LO,
) -> float:
    """
    GIVEN length-curriculum stage
    WHEN scheduling KD temperature
    THEN ramp temp_hi → temp_lo (sharper soft labels on longer seq).
    """
    f = _frac(stage, n_stages)
    return float(temp_hi) + f * (float(temp_lo) - float(temp_hi))


def decide_halat(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-ALAT vs H-CURL2 tip @ equal steps
    WHEN deciding
    THEN PROMOTE iff teacher_lp > tip; else KILL.
    """
    tip = stats.get("H-CURL2")
    if tip is None:
        return "needs H-CURL2 control"
    if float(s["mean_lp"]) > float(tip["mean_lp"]) + 1e-6:
        return "PROMOTE (beats H-CURL2 tip)"
    return "KILL (≤ H-CURL2 tip)"
