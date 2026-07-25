"""H-ABS-QPFB2: PFB K=2 on QT-int8; wall↓ vs QPFB k=4."""

from __future__ import annotations

from pfb2_ops import K2_BEAMS
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
    "decide_hqpfb2",
]


def decide_hqpfb2(
    *,
    parent_story: float,
    parent_code: float,
    qpfb2_story: float,
    qpfb2_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    qpfb2_wall: float,
    qpfb4_wall: float,
    identical: bool,
) -> str:
    """
    GIVEN QT parent vs QPFB2 + QPFB k=4 wall
    WHEN deciding H-ABS-QPFB2
    THEN dual-gate like PFB (k=2) and require wall↓ vs QPFB k=4.
    """
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=qpfb2_story,
        pfb_code=qpfb2_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=K2_BEAMS,
        identical=identical,
    )
    labeled = raw.replace("ABS-PFB k=", "ABS-QPFB2 k=", 1).replace(
        "PFB never", "QPFB2 never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    if not (float(qpfb2_wall) < float(qpfb4_wall)):
        return (
            f"KILL (wall {float(qpfb2_wall):.1f} ≥ QPFB k=4 wall "
            f"{float(qpfb4_wall):.1f})"
        )
    return labeled.replace(
        "code↑ story≥parent−ε)",
        "code↑ story≥parent−ε; wall↓ vs QPFB k=4)",
        1,
    )
