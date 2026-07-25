"""H-ABS-PFB2: PFB with K=2; dual-gate vs EARLY + wall↓ vs PFB k=4."""

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
    "K2_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "eligible_indices",
    "pick_pfb_beam",
    "unique_texts",
    "decide_hpfb2",
]

K2_BEAMS = 2


def decide_hpfb2(
    *,
    parent_story: float,
    parent_code: float,
    pfb2_story: float,
    pfb2_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    pfb2_wall: float,
    pfb4_wall: float,
    identical: bool,
) -> str:
    """
    GIVEN EARLY parent vs PFB2 + PFB k=4 wall
    WHEN deciding H-ABS-PFB2
    THEN dual-gate like PFB (k=2) and require wall↓ vs PFB k=4.
    """
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=pfb2_story,
        pfb_code=pfb2_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=K2_BEAMS,
        identical=identical,
    )
    labeled = raw.replace("ABS-PFB k=", "ABS-PFB2 k=", 1).replace(
        "PFB never", "PFB2 never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    if not (float(pfb2_wall) < float(pfb4_wall)):
        return (
            f"KILL (wall {float(pfb2_wall):.1f} ≥ PFB k=4 wall "
            f"{float(pfb4_wall):.1f})"
        )
    return labeled.replace(
        "code↑ story≥parent−ε)",
        "code↑ story≥parent−ε; wall↓ vs PFB k=4)",
        1,
    )
