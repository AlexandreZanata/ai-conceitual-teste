"""H-QG: quality-gated FLOP min vs H-EARLY (hard ε reject)."""

from __future__ import annotations

import random
from typing import Mapping, Sequence

from early_ops import EarlyGene, clamp_early_gene, mutate_early_gene
from lat_ops import EPS_LP

__all__ = [
    "EPS_LP",
    "passes_quality_gate",
    "pick_min_gflops",
    "seed_qg_from_tip",
    "decide_hqg",
]


def passes_quality_gate(lp: float, tip_lp: float, eps: float = EPS_LP) -> bool:
    """
    GIVEN candidate lp and tip lp
    WHEN applying hard quality gate
    THEN true iff lp ≥ tip_lp − ε.
    """
    return float(lp) >= float(tip_lp) - float(eps)


def pick_min_gflops(
    lps: Sequence[float],
    gflops: Sequence[float],
    tip_lp: float,
    eps: float = EPS_LP,
) -> int | None:
    """
    GIVEN scored population
    WHEN selecting among quality survivors
    THEN return index of min GFLOPs, or None if empty.
    """
    if len(lps) != len(gflops):
        raise ValueError("pick_min_gflops: length mismatch")
    eligible = [
        i for i, lp in enumerate(lps) if passes_quality_gate(lp, tip_lp, eps)
    ]
    if not eligible:
        return None
    return min(eligible, key=lambda i: float(gflops[i]))


def seed_qg_from_tip(tip: EarlyGene, rng: random.Random) -> EarlyGene:
    """
    GIVEN EARLY tip gene
    WHEN warm-starting QG
    THEN return tip or a light early mutation.
    """
    if rng.random() < 0.35:
        return mutate_early_gene(tip, rng)
    return clamp_early_gene(tip)


def decide_hqg(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-QG vs H-EARLY tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and est_gflops < EARLY; else KILL.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s.get("empty_rate", 0.0)) >= 1.0:
        return "KILL (empty quality-gated set)"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_gflops"]) < float(tip["mean_gflops"])):
        return "KILL (no FLOP win vs H-EARLY)"
    return "PROMOTE (quality-gated FLOP min vs EARLY)"
