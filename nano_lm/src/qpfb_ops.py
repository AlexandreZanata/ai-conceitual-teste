"""H-ABS-QPFB: PFB commit on QT-int8 student (parent = H-QT)."""

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
    "decide_hqpfb",
]


def decide_hqpfb(
    *,
    parent_story: float,
    parent_code: float,
    qpfb_story: float,
    qpfb_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    k: int,
    identical: bool,
) -> str:
    """
    GIVEN QT parent vs QPFB dual means
    WHEN deciding H-ABS-QPFB
    THEN same dual gate as PFB, labeled ABS-QPFB (parent = H-QT).
    """
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=qpfb_story,
        pfb_code=qpfb_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=k,
        identical=identical,
    )
    return (
        raw.replace("ABS-PFB", "ABS-QPFB")
        .replace("PFB never", "QPFB never")
    )