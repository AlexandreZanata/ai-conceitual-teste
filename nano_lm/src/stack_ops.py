"""H-STACK: H-EARLY × H-DECM dual tip; dual-gate vs max tip."""

from __future__ import annotations

from typing import Mapping

from early_ops import EarlyGene, clamp_early_gene
from lat_ops import EPS_LP

__all__ = ["MIX_M", "early_gene_key", "decide_hstack"]

MIX_M = 3


def early_gene_key(gene: EarlyGene) -> tuple:
    g = clamp_early_gene(gene)
    return (
        int(g["min_new"]),
        int(g["patience"]),
        round(float(g["conf_threshold"]), 3),
        int(g["n"]),
        round(float(g["temperature"]), 3),
        round(float(g["top_p"]), 3),
    )


def decide_hstack(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-STACK vs H-EARLY and H-DECM tips
    WHEN deciding
    THEN PROMOTE only if lp ≥ max(tips)−ε and wall < min(tips); else KILL.
    """
    early = stats.get("H-EARLY")
    decm = stats.get("H-DECM")
    if early is None or decm is None:
        return "needs H-EARLY+H-DECM controls"
    max_lp = max(float(early["mean_lp"]), float(decm["mean_lp"]))
    min_wall = min(float(early["mean_wall"]), float(decm["mean_wall"]))
    if float(s["mean_lp"]) < max_lp - EPS_LP:
        return "KILL (≤ max tip quality)"
    if not (float(s["mean_wall"]) < min_wall):
        return "KILL (no dual wall win)"
    return "PROMOTE (dual win vs tips)"
