"""H-CHB: sweep chunk_size B vs H-CHUNK tip; wall gate."""

from __future__ import annotations

from typing import Mapping, Sequence

from chunk_ops import DEFAULT_CHUNK
from lat_ops import EPS_LP

__all__ = [
    "SMOKE_SIZES",
    "DEFAULT_CHUNK",
    "decide_hchb",
    "pick_chb_size",
    "EPS_LP",
]

# Tip DEFAULT_CHUNK=32 is included so equal-best → KILL (no wall win).
SMOKE_SIZES: tuple[int, ...] = (32, 64, 128, 256)


def pick_chb_size(
    scored: Mapping[int, Mapping[str, float]],
    *,
    early_lp: float,
    eps_lp: float = EPS_LP,
) -> int:
    """
    GIVEN per-B metrics
    WHEN selecting
    THEN prefer quality-ok (lp ≥ EARLY−ε) with min wall; else min wall overall.
    """
    if not scored:
        raise ValueError("pick_chb_size: empty scored")
    ok = [
        b
        for b, m in scored.items()
        if float(m["mean_lp"]) >= float(early_lp) - float(eps_lp)
    ]
    pool: Sequence[int] = ok if ok else list(scored.keys())
    return min(pool, key=lambda b: float(scored[b]["mean_wall"]))


def decide_hchb(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-CHB best-B vs H-EARLY / H-CHUNK tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ EARLY−ε and wall < CHUNK tip; else KILL.
    """
    early = stats.get("H-EARLY")
    tip = stats.get("H-CHUNK")
    if early is None:
        return "needs H-EARLY control"
    if tip is None:
        return "needs H-CHUNK control"
    if float(s["mean_lp"]) < float(early["mean_lp"]) - float(eps_lp):
        return "KILL (quality drop vs H-EARLY)"
    if not (float(s["mean_wall"]) < float(tip["mean_wall"])):
        return "KILL (best ≤ tip wall; no chunk_size win)"
    return "PROMOTE (chunk_size sweep beats H-CHUNK tip)"
