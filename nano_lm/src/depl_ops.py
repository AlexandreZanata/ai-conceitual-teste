"""H-DEPL: runnable deploy policy gated on H-BUD survivors."""

from __future__ import annotations

from typing import Mapping, Sequence

from bud_ops import BUD_RECIPES

__all__ = [
    "BUD_RECIPES",
    "DEPL_GOALS",
    "DEPL_SCENARIOS",
    "choose_recipe",
    "scenario_ok",
    "decide_hdepl",
]

DEPL_GOALS = ("speed", "quality", "train")

# Canonical intents from RECIPES.md + XFER2 bound.
DEPL_SCENARIOS: tuple[dict[str, object], ...] = (
    {"id": "speed_in_dist", "goal": "speed", "in_dist": True, "ood_long": False},
    {"id": "speed_ood_long", "goal": "speed", "in_dist": False, "ood_long": True},
    {"id": "quality_in_dist", "goal": "quality", "in_dist": True, "ood_long": False},
    {"id": "quality_ood", "goal": "quality", "in_dist": False, "ood_long": False},
    {"id": "train_steps", "goal": "train", "in_dist": True, "ood_long": False},
)


def choose_recipe(
    *,
    goal: str,
    in_dist: bool,
    ood_long: bool = False,
) -> str:
    """
    GIVEN deploy intent + distribution flags
    WHEN applying frozen RECIPES policy
    THEN return H-PACK / H-QPACK / H-TPACK or REJECT reason.
    """
    g = str(goal)
    if g not in DEPL_GOALS:
        return "needs goal speed|quality|train"
    if g == "speed":
        if bool(ood_long):
            return "REJECT (PACK forbidden on ood_long)"
        return "H-PACK"
    if g == "quality":
        if not bool(in_dist):
            return "REJECT (QPACK requires in-dist)"
        return "H-QPACK"
    return "H-TPACK"


def scenario_ok(
    choice: str,
    bud_verdicts: Mapping[str, str],
) -> bool:
    """
    GIVEN policy choice + BUD per-recipe strings
    WHEN checking consistency
    THEN True iff REJECT or chosen recipe SURVIVEs under BUD.
    """
    if str(choice).startswith("REJECT"):
        return True
    if str(choice).startswith("needs"):
        return False
    v = bud_verdicts.get(choice)
    return v is not None and str(v).startswith("SURVIVE")


def decide_hdepl(
    bud_verdicts: Mapping[str, str],
    *,
    scenarios: Sequence[Mapping[str, object]] = DEPL_SCENARIOS,
) -> str:
    """
    GIVEN BUD survivors + deploy scenarios
    WHEN applying runnable policy
    THEN PROMOTE iff every scenario is REJECT or a BUD SURVIVE recipe;
         else KILL naming the first contradicting scenario.
    """
    for recipe in BUD_RECIPES:
        if recipe not in bud_verdicts:
            return f"needs {recipe} BUD verdict"
    routes: list[str] = []
    for sc in scenarios:
        sid = str(sc.get("id", "scenario"))
        choice = choose_recipe(
            goal=str(sc["goal"]),
            in_dist=bool(sc.get("in_dist", False)),
            ood_long=bool(sc.get("ood_long", False)),
        )
        if not scenario_ok(choice, bud_verdicts):
            return f"KILL (policy contradicts BUD on {sid}: {choice})"
        routes.append(f"{sid}→{choice}")
    return f"PROMOTE (deploy policy consistent: {';'.join(routes)})"
