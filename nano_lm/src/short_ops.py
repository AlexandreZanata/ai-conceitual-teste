"""H-SHORT: two-phase short draft → continue only if conf low."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP

__all__ = [
    "DRAFT_MAXS",
    "STOP_CONFS",
    "ShortGene",
    "clamp_short_gene",
    "random_short_gene",
    "mutate_short_gene",
    "should_stop_after_draft",
    "decide_hshort",
]

ShortGene = dict[str, Any]
DRAFT_MAXS = (4, 8, 12)
STOP_CONFS = (0.55, 0.7, 0.85)


def should_stop_after_draft(*, draft_done: bool, max_p: float, stop_conf: float) -> bool:
    """
    GIVEN draft phase complete and last-token max probability
    WHEN checking adaptive stop
    THEN true iff draft done and max_p ≥ stop_conf (high confidence).
    """
    return bool(draft_done) and float(max_p) >= float(stop_conf)


def clamp_short_gene(gene: Mapping[str, Any], tip: Mapping[str, Any]) -> ShortGene:
    out = dict(tip)
    out["draft_max"] = int(min(DRAFT_MAXS, key=lambda x: abs(x - int(gene["draft_max"]))))
    out["stop_conf"] = float(min(STOP_CONFS, key=lambda x: abs(x - float(gene["stop_conf"]))))
    return out


def random_short_gene(rng: random.Random, tip: Mapping[str, Any]) -> ShortGene:
    return clamp_short_gene(
        {"draft_max": rng.choice(DRAFT_MAXS), "stop_conf": rng.choice(STOP_CONFS)},
        tip,
    )


def mutate_short_gene(gene: ShortGene, rng: random.Random, tip: Mapping[str, Any]) -> ShortGene:
    g = dict(gene)
    if rng.random() < 0.5:
        g["draft_max"] = rng.choice(DRAFT_MAXS)
    else:
        g["stop_conf"] = rng.choice(STOP_CONFS)
    return clamp_short_gene(g, tip)


def decide_hshort(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-SHORT vs H-EARLY tip
    WHEN deciding
    THEN KILL if quality cliff or dominated on (wall, GFLOPs); else PROMOTE.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY)"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    flop_win = float(s["mean_gflops"]) < float(tip["mean_gflops"])
    if not wall_win and not flop_win:
        return "KILL (dominated on wall+GFLOPs)"
    return "PROMOTE (adaptive short draft vs EARLY)"