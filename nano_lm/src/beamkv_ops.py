"""H-BEAMKV: shared prompt KV across PFB K beams; wall↓ vs indep prefills."""

from __future__ import annotations

from pfb2_ops import K2_BEAMS
from pfb_ops import (
    EPS_LP,
    MIN_UNIQUE,
    PFB_TEMP,
    decide_hpfb,
    eligible_indices,
    pick_pfb_beam,
    unique_texts,
)

__all__ = [
    "K2_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "eligible_indices",
    "pick_pfb_beam",
    "unique_texts",
    "decide_hbeamkv",
]


def decide_hbeamkv(
    *,
    parent_story: float,
    parent_code: float,
    beamkv_story: float,
    beamkv_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    beamkv_wall: float,
    naive_wall: float,
    identical: bool,
) -> str:
    """
    GIVEN QT parent vs BEAMKV + naive indep-prefill wall
    WHEN deciding H-BEAMKV
    THEN dual-gate like QPFB2 (k=2) and require wall↓ vs naive.
    """
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=beamkv_story,
        pfb_code=beamkv_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=K2_BEAMS,
        identical=identical,
    )
    labeled = raw.replace("ABS-PFB k=", "BEAMKV k=", 1).replace(
        "PFB never", "BEAMKV never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    if not (float(beamkv_wall) < float(naive_wall)):
        return (
            f"KILL (wall {float(beamkv_wall):.1f} ≥ naive indep wall "
            f"{float(naive_wall):.1f})"
        )
    return labeled.replace(
        "code↑ story≥parent−ε)",
        "code↑ story≥parent−ε; wall↓ vs indep prefills)",
        1,
    )
