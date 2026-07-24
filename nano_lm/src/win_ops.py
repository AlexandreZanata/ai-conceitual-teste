"""H-WIN: sliding-window attention gate vs H-STAG (quality@FLOPs)."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "DEFAULT_WINDOW",
    "TIP_STAGES",
    "scale_flops_for_window",
    "decide_hwin",
    "EPS_LP",
]

DEFAULT_WINDOW = 32
TIP_STAGES = 4
_ATTN_FRAC = 0.25


def scale_flops_for_window(
    full_flops: float, *, seq_len: int, window: int, attn_frac: float = _ATTN_FRAC
) -> float:
    """
    GIVEN dense FLOP estimate, sequence length, and local window
    WHEN scaling attention portion
    THEN attn_frac scales by min(1, window/seq); rest unchanged.
    """
    seq = max(1, int(seq_len))
    win = max(1, int(window))
    ratio = min(1.0, float(win) / float(seq))
    frac = min(1.0, max(0.0, float(attn_frac)))
    return float(full_flops) * ((1.0 - frac) + frac * ratio)


def decide_hwin(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-WIN vs H-STAG tip
    WHEN deciding
    THEN PROMOTE iff lp ≥ STAG−ε and est_gflops < STAG; else KILL.
    """
    tip = stats.get("H-STAG")
    if tip is None:
        return "needs H-STAG control"
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - EPS_LP:
        return "KILL (quality drop vs H-STAG)"
    if not (float(s["mean_gflops"]) < float(tip["mean_gflops"])):
        return "KILL (no FLOP win vs H-STAG)"
    return "PROMOTE (window attn vs STAG)"
