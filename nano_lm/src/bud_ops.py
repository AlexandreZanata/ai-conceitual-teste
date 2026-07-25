"""H-BUD: hard wall/GFLOPs (or ms/step) budget gate vs tip for official recipes."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from pareto_ops import DELTA_GFLOPS_FRAC

__all__ = [
    "DELTA_GFLOPS_FRAC",
    "EPS_LP",
    "BUD_RECIPES",
    "within_wall_budget",
    "within_gflops_budget",
    "within_ms_step_budget",
    "survive_decode",
    "survive_train",
    "decide_hbud",
]

BUD_RECIPES = ("H-PACK", "H-QPACK", "H-TPACK")


def within_wall_budget(util: Mapping[str, float], tip: Mapping[str, float]) -> bool:
    """Fixed wall budget = tip mean_wall; util must not exceed tip."""
    return float(util["mean_wall"]) <= float(tip["mean_wall"])


def within_gflops_budget(
    util: Mapping[str, float],
    tip: Mapping[str, float],
    *,
    delta_frac: float = DELTA_GFLOPS_FRAC,
) -> bool:
    """Fixed GFLOPs budget = tip·(1+δ); util must not exceed ceiling."""
    ceiling = float(tip["mean_gflops"]) * (1.0 + float(delta_frac))
    return float(util["mean_gflops"]) <= ceiling


def within_ms_step_budget(util: Mapping[str, float], tip: Mapping[str, float]) -> bool:
    """Train analogue of wall: ms/step ≤ tip ms/step."""
    return float(util["mean_ms_step"]) <= float(tip["mean_ms_step"])


def survive_decode(
    util: Mapping[str, float],
    tip: Mapping[str, float],
    *,
    eps_lp: float = EPS_LP,
    delta_frac: float = DELTA_GFLOPS_FRAC,
) -> str:
    """
    GIVEN decode recipe util vs tip
    WHEN applying hard wall + GFLOPs budgets
    THEN SURVIVE iff quality floor, both budgets, and wall↓ or tok/s↑.
    """
    if float(util["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop under budget)"
    if not within_wall_budget(util, tip):
        return "KILL (wall over tip budget)"
    if not within_gflops_budget(util, tip, delta_frac=delta_frac):
        return "KILL (GFLOPs over tip budget)"
    wall_win = float(util["mean_wall"]) < float(tip["mean_wall"])
    tps_win = float(util["mean_tps"]) > float(tip["mean_tps"])
    if not (wall_win or tps_win):
        return "KILL (no wall/tok/s win under budget)"
    return "SURVIVE (wall+GFLOPs budgets + win)"


def survive_train(
    util: Mapping[str, float],
    tip: Mapping[str, float],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN train recipe util vs tip
    WHEN applying hard ms/step budget
    THEN SURVIVE iff quality floor and ms/step < tip (strict win inside budget).
    """
    if float(util["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop under budget)"
    if not within_ms_step_budget(util, tip):
        return "KILL (ms/step over tip budget)"
    if not (float(util["mean_ms_step"]) < float(tip["mean_ms_step"])):
        return "KILL (no ms/step win under budget)"
    return "SURVIVE (ms/step budget + win)"


def decide_hbud(verdicts: Mapping[str, str]) -> str:
    """
    GIVEN per-recipe SURVIVE/KILL strings
    WHEN aggregating budget Pareto hard gate
    THEN PROMOTE iff ≥1 recipe SURVIVE; else KILL.
    """
    survivors: list[str] = []
    for recipe in BUD_RECIPES:
        v = verdicts.get(recipe)
        if v is None:
            return f"needs {recipe} verdict"
        if str(v).startswith("SURVIVE"):
            survivors.append(recipe)
    if not survivors:
        return "KILL (no recipe beats tip under wall/GFLOPs budget)"
    joined = "+".join(survivors)
    return f"PROMOTE (budget survivors: {joined})"
