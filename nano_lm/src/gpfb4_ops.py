"""H-ABS-GPFB4: PFB K=4 under frozen GENC genome (≠ GPFB K=2)."""

from __future__ import annotations

from pfb_ops import (
    EPS_LP,
    K_BEAMS,
    MIN_UNIQUE,
    PFB_TEMP,
    decide_hpfb,
    eligible_indices,
    pick_pfb_beam,
    unique_texts,
)

__all__ = [
    "K_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "eligible_indices",
    "pick_pfb_beam",
    "unique_texts",
    "decide_hgpfb4",
]


def decide_hgpfb4(
    *,
    parent_story: float,
    parent_code: float,
    gpfb4_story: float,
    gpfb4_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    k: int,
    identical: bool,
) -> str:
    """
    GIVEN GENC-serial parent vs GPFB4 K=4 PFB commit
    WHEN deciding H-ABS-GPFB4
    THEN dual-gate like PFB labeled for GENC∘PFB k=4 (no wall↓ vs k=2).
    """
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=gpfb4_story,
        pfb_code=gpfb4_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=k,
        identical=identical,
    )
    return (
        raw.replace("ABS-PFB k=", "ABS-GPFB4 k=", 1)
        .replace("PFB never", "GPFB4 never", 1)
    )
