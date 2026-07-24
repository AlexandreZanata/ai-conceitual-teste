"""H-KVSEL: enable past_key_values only when max_new > threshold."""

from __future__ import annotations

from typing import Mapping, TypedDict

from flop_ops import est_decode_flops
from lat_ops import EPS_LP

__all__ = [
    "KvselGene",
    "SMOKE_BUDGETS",
    "SMOKE_THRESHOLDS",
    "should_use_kv",
    "clamp_kvsel_gene",
    "est_kvsel_flops",
    "decide_hkvsel",
]


class KvselGene(TypedDict):
    kv_threshold: int


SMOKE_BUDGETS: tuple[int, ...] = (16, 64)
# Each thr enables KV on at least the long budget (max_new > thr).
SMOKE_THRESHOLDS: tuple[int, ...] = (0, 16, 32, 48)


def should_use_kv(max_new: int, kv_threshold: int) -> bool:
    """
    GIVEN decode budget and threshold gene
    WHEN selecting backend
    THEN use KV iff max_new > kv_threshold.
    """
    return int(max_new) > int(kv_threshold)


def clamp_kvsel_gene(gene: Mapping[str, object]) -> KvselGene:
    thr = int(gene.get("kv_threshold", 32))
    return {"kv_threshold": max(0, min(512, thr))}


def est_kvsel_flops(
    *,
    n_params: int,
    prompt_len: int,
    n_new: int,
    use_kv: bool,
) -> float:
    """
    GIVEN lengths and KV flag
    WHEN estimating decode FLOPs
    THEN triangular uncached sum, or 2N(p+t) KV proxy.
    """
    if not use_kv:
        return est_decode_flops(
            n_params=n_params, prompt_len=prompt_len, n_new=n_new
        )
    n = int(n_params)
    p = max(0, int(prompt_len))
    t = max(0, int(n_new))
    if n < 1 or t < 1:
        return 0.0
    return 2.0 * float(n) * float(p + t)


def decide_hkvsel(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-KVSEL vs H-EARLY tip (dual-budget mean)
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and wall < EARLY.
    """
    tip = stats.get("H-EARLY")
    if tip is None:
        return "needs H-EARLY control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (no wall win vs H-EARLY)"
    return "PROMOTE (gated KV vs EARLY)"
