"""H-PARETO: flag tok/s↑ with GFLOPs↑ beyond tip+δ (honest efficiency)."""

from __future__ import annotations

from typing import Mapping

__all__ = [
    "DELTA_GFLOPS_FRAC",
    "is_efficiency_inflated",
    "classify_util",
    "decide_hpareto",
]

# Relative GFLOPs slack vs tip; beyond tip*(1+δ) counts as inflate.
DELTA_GFLOPS_FRAC = 0.05


def is_efficiency_inflated(
    util: Mapping[str, float],
    tip: Mapping[str, float],
    *,
    delta_frac: float = DELTA_GFLOPS_FRAC,
) -> bool:
    """
    GIVEN util and tip mean_tps / mean_gflops
    WHEN checking dishonest speed claims
    THEN True iff tok/s↑ and GFLOPs > tip·(1+δ).
    """
    tip_tps = float(tip["mean_tps"])
    tip_gf = float(tip["mean_gflops"])
    util_tps = float(util["mean_tps"])
    util_gf = float(util["mean_gflops"])
    tps_up = util_tps > tip_tps
    gf_ceiling = tip_gf * (1.0 + float(delta_frac))
    gf_up = util_gf > gf_ceiling
    return bool(tps_up and gf_up)


def classify_util(
    util: Mapping[str, float],
    tip: Mapping[str, float],
    *,
    delta_frac: float = DELTA_GFLOPS_FRAC,
) -> str:
    """
    GIVEN util vs tip metrics
    WHEN classifying
    THEN FLAG if inflated; else KEEP.
    """
    if is_efficiency_inflated(util, tip, delta_frac=delta_frac):
        return "FLAG (tok/s↑ but GFLOPs↑ beyond tip+δ)"
    return "KEEP (honest or no tps↑/GFLOPs↑ claim)"


def decide_hpareto(*, n_pairs: int, n_flagged: int) -> str:
    """
    GIVEN Pareto audit pair counts
    WHEN deciding (instrumentation gate)
    THEN PROMOTE iff ≥1 pair classified; else KILL.
    """
    if int(n_pairs) < 1:
        return "KILL (no util/tip pairs with GFLOPs)"
    return f"PROMOTE (Pareto audit live; {int(n_flagged)} flagged)"
