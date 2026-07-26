"""H-ROLL: rolling W + summary tokens; PFB per segment; mem≈O(W)."""

from __future__ import annotations

from pfb2_ops import K2_BEAMS
from pfb_ops import EPS_LP, MIN_UNIQUE, PFB_TEMP, decide_hpfb

__all__ = [
    "K2_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "ROLL_W",
    "ROLL_S",
    "ROLL_TARGET",
    "MIN_LEFF_RATIO",
    "decide_hroll",
]

ROLL_W = 128
ROLL_S = 32
ROLL_TARGET = 384  # L_eff ≫ W (ratio ≥ 3)
MIN_LEFF_RATIO = 3.0


def decide_hroll(
    *,
    parent_story: float,
    parent_code: float,
    roll_story: float,
    roll_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    l_eff: float,
    mean_active: float,
    w: int = ROLL_W,
    s: int = ROLL_S,
    identical: bool,
) -> str:
    """
    GIVEN EARLY vs PFB2 on rolled ctx + L_eff/active
    WHEN deciding H-ROLL
    THEN dual gate; require L_eff ≥ ratio·W and active ≤ W+S.
    """
    need = float(MIN_LEFF_RATIO) * float(w)
    if float(l_eff) < need:
        return (
            f"KILL (L_eff {float(l_eff):.0f} < {MIN_LEFF_RATIO:g}·W "
            f"={need:.0f})"
        )
    cap = float(w) + float(s)
    if float(mean_active) > cap + 1e-6:
        return (
            f"KILL (mean_active {float(mean_active):.0f} > W+S={cap:.0f}; "
            f"mem not O(W))"
        )
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=roll_story,
        pfb_code=roll_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=K2_BEAMS,
        identical=identical,
    )
    labeled = raw.replace("ABS-PFB k=", "ROLL k=", 1).replace(
        "PFB never", "ROLL never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    return labeled.replace(
        "code↑ story≥parent−ε)",
        (
            f"code↑ story≥parent−ε; L_eff={float(l_eff):.0f}≫W={int(w)}; "
            f"active={float(mean_active):.0f}≤W+S={int(w)+int(s)})"
        ),
        1,
    )
