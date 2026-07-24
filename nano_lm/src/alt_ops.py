"""H-ALT: alternate full vs shallow depth every N tokens under EARLY."""

from __future__ import annotations

import random
from typing import Any, Mapping

from lat_ops import EPS_LP

__all__ = [
    "ALT_PERIODS",
    "SHALLOW_SKIPS",
    "AltGene",
    "clamp_alt_gene",
    "random_alt_gene",
    "mutate_alt_gene",
    "use_shallow_step",
    "decide_halt",
]

AltGene = dict[str, Any]
ALT_PERIODS = (1, 2, 4)
SHALLOW_SKIPS = (1,)


def use_shallow_step(
    *, step: int, period: int, start_shallow: bool
) -> bool:
    """
    GIVEN decode step index and alternate period
    WHEN choosing depth
    THEN True on shallow half-cycles (period blocks of steps).
    """
    if int(period) < 1:
        raise ValueError("period must be >= 1")
    phase = (int(step) // int(period)) % 2
    return bool(phase == 0) if bool(start_shallow) else bool(phase == 1)


def clamp_alt_gene(gene: Mapping[str, Any], tip: Mapping[str, Any]) -> AltGene:
    out = dict(tip)
    per = int(round(float(gene["alt_period"])))
    out["alt_period"] = int(min(ALT_PERIODS, key=lambda x: abs(x - per)))
    sk = int(round(float(gene["shallow_skip"])))
    out["shallow_skip"] = int(min(SHALLOW_SKIPS, key=lambda x: abs(x - sk)))
    out["start_shallow"] = int(1 if int(gene.get("start_shallow", 0)) else 0)
    return out


def random_alt_gene(rng: random.Random, tip: Mapping[str, Any]) -> AltGene:
    return clamp_alt_gene(
        {
            "alt_period": rng.choice(ALT_PERIODS),
            "shallow_skip": rng.choice(SHALLOW_SKIPS),
            "start_shallow": rng.choice([0, 1]),
        },
        tip,
    )


def mutate_alt_gene(
    gene: AltGene, rng: random.Random, tip: Mapping[str, Any]
) -> AltGene:
    g = dict(gene)
    r = rng.random()
    if r < 0.4:
        g["alt_period"] = rng.choice(ALT_PERIODS)
    elif r < 0.7:
        g["start_shallow"] = 1 - int(g.get("start_shallow", 0))
    else:
        g["shallow_skip"] = rng.choice(SHALLOW_SKIPS)
    return clamp_alt_gene(g, tip)


def decide_halt(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-ALT vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and (wall < EARLY or gflops < EARLY).
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY)"
    wall_win = float(s["mean_wall"]) < float(tip["mean_wall"])
    flop_win = float(s["mean_gflops"]) < float(tip["mean_gflops"])
    if not (wall_win or flop_win):
        return "KILL (no wall/GFLOPs win vs H-EARLY)"
    return "PROMOTE (alternate depth vs EARLY)"
