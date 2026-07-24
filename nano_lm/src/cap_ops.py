"""H-CAP: hard max_new/n caps on H-POOL tip genes."""

from __future__ import annotations

from typing import Mapping

from decode_genes import Gene, clamp_gene
from lat_ops import EPS_LP

__all__ = ["CAP_NEWS", "CAP_MAX_N", "apply_hard_caps", "decide_hcap"]

CAP_NEWS = (8, 12, 16)
CAP_MAX_N = 2


def apply_hard_caps(gene: Gene, max_new: int) -> tuple[Gene, int]:
    """
    GIVEN a POOL tip gene and candidate max_new
    WHEN applying hard caps
    THEN n ≤ CAP_MAX_N and max_new snapped to CAP_NEWS.
    """
    g = dict(clamp_gene(gene))
    g["n"] = int(min(CAP_MAX_N, max(1, int(g["n"]))))
    mn = int(round(float(max_new)))
    capped = min(CAP_NEWS, key=lambda x: abs(x - mn))
    return clamp_gene(g), int(capped)


def decide_hcap(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-CAP vs H-POOL
    WHEN deciding
    THEN PROMOTE iff quality ≥ POOL−ε and wall < POOL; else KILL.
    """
    tip = stats.get("H-POOL")
    if tip is None:
        return "needs H-POOL control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality < POOL−ε)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall save vs H-POOL)"
    return "PROMOTE (hard caps wall vs H-POOL)"
