"""H-STEP: early-stop KD plateau helpers; decide vs H-CURL2 tip."""

from __future__ import annotations

from typing import Mapping

__all__ = ["improved", "should_stop", "decide_hstep"]


def improved(metric: float, best: float, *, min_delta: float) -> bool:
    """
    GIVEN higher-is-better metric (teacher_lp)
    WHEN checking improvement
    THEN true iff metric > best + min_delta.
    """
    return float(metric) > float(best) + float(min_delta)


def should_stop(bad_streak: int, *, patience: int) -> bool:
    """
    GIVEN consecutive non-improving val checks
    WHEN deciding early stop
    THEN true iff bad_streak ≥ patience.
    """
    if int(patience) < 1:
        raise ValueError("should_stop: patience must be >= 1")
    return int(bad_streak) >= int(patience)


def decide_hstep(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-STEP vs H-CURL2 tip @ same max step budget
    WHEN deciding
    THEN PROMOTE iff teacher_lp ≥ tip; else KILL (worse).
    """
    tip = stats.get("H-CURL2")
    if tip is None:
        return "needs H-CURL2 control"
    if float(s["mean_lp"]) + 1e-6 < float(tip["mean_lp"]):
        return "KILL (worse than H-CURL2 tip)"
    return "PROMOTE (lp ≥ H-CURL2 tip @ early-stop)"
