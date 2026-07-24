"""H-TOPK: sweep top-k width vs tip k=64 on (lp, ms/step)."""

from __future__ import annotations

from typing import Mapping, Sequence

from lat_ops import EPS_LP
from top_ops import DEFAULT_TOP_K

__all__ = [
    "TOPK_SWEEP",
    "TIP_TOP_K",
    "SMOKE_BEST_K",
    "beats_tip_k",
    "decide_htopk",
    "slice_topk_records",
]

TOPK_SWEEP = (16, 32, 64, 128)
TIP_TOP_K = DEFAULT_TOP_K
# Smoke winner (htopk-vs-htop.md); formal compares this vs tip only.
SMOKE_BEST_K = 32


def slice_topk_records(records: Sequence[dict], k: int) -> list[dict]:
    """
    GIVEN a max-width top-k cache (sorted descending)
    WHEN slicing to width k
    THEN return records with exact top-k indices/values.
    """
    width = int(k)
    if width < 1:
        raise ValueError("k must be >= 1")
    out: list[dict] = []
    for rec in records:
        idx = rec["topk_idx"]
        if width > int(idx.shape[-1]):
            raise ValueError("k exceeds cached width")
        out.append(
            {
                "ids": rec["ids"],
                "topk_idx": idx[..., :width].contiguous(),
                "topk_val": rec["topk_val"][..., :width].contiguous(),
            }
        )
    return out


def beats_tip_k(
    s: Mapping[str, float],
    tip: Mapping[str, float],
    *,
    eps_lp: float = EPS_LP,
) -> bool:
    """True iff lp ≥ tip−ε and ms/step < tip."""
    if float(s["mean_lp"]) < float(tip["mean_lp"]) - float(eps_lp):
        return False
    return float(s["mean_ms_step"]) < float(tip["mean_ms_step"])


def decide_htopk(
    by_k: Mapping[int, Mapping[str, float]],
    *,
    tip_k: int = TIP_TOP_K,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN H-TOPK sweep vs tip k=64
    WHEN deciding
    THEN PROMOTE iff some k≠tip beats tip on (lp, ms/step); else KILL.
    """
    tip = by_k.get(int(tip_k))
    if tip is None:
        return f"needs tip k={tip_k}"
    winners = [
        int(k)
        for k, s in by_k.items()
        if int(k) != int(tip_k) and beats_tip_k(s, tip, eps_lp=eps_lp)
    ]
    if not winners:
        return "KILL (best ≤ tip k=64 on lp, ms/step)"
    best = min(
        winners,
        key=lambda k: (float(by_k[k]["mean_ms_step"]), -float(by_k[k]["mean_lp"])),
    )
    return f"PROMOTE (best k={best} beats tip k={tip_k})"
