"""H-PFB256: PFB2 on elongated L=256 prompts (not CTX chunked-KV)."""

from __future__ import annotations

from chunk_ops import LONG_TARGET_TOKENS
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
    "PFB256_TARGET",
    "REF128_TARGET",
    "eligible_indices",
    "pick_pfb_beam",
    "unique_texts",
    "decide_hpfb256",
]

PFB256_TARGET = 256
REF128_TARGET = int(LONG_TARGET_TOKENS)  # tip pack = 128


def decide_hpfb256(
    *,
    parent_story: float,
    parent_code: float,
    pfb256_story: float,
    pfb256_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    wall_256: float,
    wall_128: float,
    identical: bool,
) -> str:
    """
    GIVEN EARLY@256 vs PFB2@256 + wall@128 reference
    WHEN deciding H-PFB256
    THEN dual-gate like PFB (k=2); report wall@256 vs @128 (no CTX claim).
    """
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=pfb256_story,
        pfb_code=pfb256_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=K2_BEAMS,
        identical=identical,
    )
    labeled = raw.replace("ABS-PFB k=", "PFB256 k=", 1).replace(
        "PFB never", "PFB256 never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    return labeled.replace(
        "code↑ story≥parent−ε)",
        (
            f"code↑ story≥parent−ε; wall@256={float(wall_256):.0f} "
            f"vs @128={float(wall_128):.0f})"
        ),
        1,
    )
