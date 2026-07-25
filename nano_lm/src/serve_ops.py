"""H-SERVE: frozen full serving stack vs tip H-EARLY alone."""

from __future__ import annotations

from typing import Mapping

from chbat_ops import CHBAT_CHUNK
from lat_ops import EPS_LP

__all__ = [
    "decide_hserve",
    "pick_serve_recipe",
    "SERVE_CHUNK",
    "SERVE_RECIPES",
    "EPS_LP",
]

# CHB formal winner under batch/systems stacks.
SERVE_CHUNK = CHBAT_CHUNK
SERVE_RECIPES = ("speed", "quality")


def pick_serve_recipe(
    cands: Mapping[str, Mapping[str, float]],
    *,
    early_lp: float,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN speed (GALL) and quality (GRAPHF) candidate metrics
    WHEN selecting the serving recipe
    THEN prefer |Δlp|≤ε vs EARLY with min wall; else min wall overall.
    """
    if not cands:
        raise ValueError("pick_serve_recipe: empty candidates")
    ok = [
        name
        for name, m in cands.items()
        if abs(float(m["mean_lp"]) - float(early_lp)) <= float(eps_lp)
    ]
    pool = ok if ok else list(cands.keys())
    return min(pool, key=lambda n: float(cands[n]["mean_wall_ms"]))


def decide_hserve(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-SERVE (best frozen stack) vs H-EARLY tip alone
    WHEN deciding
    THEN PROMOTE iff |Δlp| ≤ ε and (wall < EARLY or tok/s > EARLY).
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if abs(float(s["mean_lp"]) - float(tip["mean_lp"])) > float(eps_lp):
        return "KILL (lp change vs H-EARLY)"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    tps_win = float(s["mean_tps"]) > float(tip["mean_tps"])
    if not (wall_win or tps_win):
        return "KILL (no wall/tok/s win vs H-EARLY)"
    return "PROMOTE (full serving stack vs EARLY)"
