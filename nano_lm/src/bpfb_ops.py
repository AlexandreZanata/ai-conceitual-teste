"""H-ABS-BPFB: PFB2 on bitcoin pack; dual-gate + wall↓ vs k=4."""

from __future__ import annotations

from pfb2_ops import K2_BEAMS, decide_hpfb2
from pfb_ops import (
    EPS_LP,
    K_BEAMS,
    MIN_UNIQUE,
    PFB_TEMP,
    eligible_indices,
    pick_pfb_beam,
    unique_texts,
)

__all__ = [
    "K_BEAMS",
    "K2_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "eligible_indices",
    "pick_pfb_beam",
    "unique_texts",
    "decide_hbpfb",
]


def decide_hbpfb(
    *,
    parent_story: float,
    parent_code: float,
    bpfb_story: float,
    bpfb_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    bpfb_wall: float,
    bpfb4_wall: float,
    identical: bool,
) -> str:
    """
    GIVEN EARLY@BTC vs BPFB K=2 + k=4 wall
    WHEN deciding H-ABS-BPFB
    THEN dual-gate like PFB2 labeled for bitcoin pack.
    """
    raw = decide_hpfb2(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb2_story=bpfb_story,
        pfb2_code=bpfb_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        pfb2_wall=bpfb_wall,
        pfb4_wall=bpfb4_wall,
        identical=identical,
    )
    return (
        raw.replace("ABS-PFB2 k=", "ABS-BPFB k=", 1)
        .replace("PFB2 never", "BPFB never", 1)
        .replace("vs PFB k=4", "vs BPFB k=4")
        .replace("≥ PFB k=4 wall", "≥ BPFB k=4 wall")
    )
