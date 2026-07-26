"""H-GPFB4-LONG: GPFB4 (K=4) on ROLL/PFB256 ctx; wall budget; never K=2."""

from __future__ import annotations

from gpfb4_ops import decide_hgpfb4
from pfb_ops import EPS_LP, K_BEAMS, MIN_UNIQUE, PFB_TEMP
from roll_ops import MIN_LEFF_RATIO, ROLL_S, ROLL_TARGET, ROLL_W

__all__ = [
    "K_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "ROLL_W",
    "ROLL_S",
    "ROLL_TARGET",
    "MIN_LEFF_RATIO",
    "WALL_SLACK_MS",
    "require_k4",
    "decide_hgpfb4long",
]

WALL_SLACK_MS = 5.0  # nano noise; reject clear slowdowns vs full-prefill


def require_k4(k: int) -> str | None:
    """
    GIVEN beam count
    WHEN guarding GPFB-K=2 pathology
    THEN None iff k==4; else KILL reason.
    """
    if int(k) != int(K_BEAMS):
        return (
            f"KILL (k={int(k)} ≠ {K_BEAMS}; GPFB-K=2 pathology forbidden)"
        )
    return None


def decide_hgpfb4long(
    *,
    parent_story: float,
    parent_code: float,
    long_story: float,
    long_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    k: int,
    identical: bool,
    l_eff: float,
    mean_active: float,
    wall_roll: float,
    wall_full: float,
    w: int = ROLL_W,
    s: int = ROLL_S,
    wall_slack_ms: float = WALL_SLACK_MS,
) -> str:
    """
    GIVEN GENC-serial vs GPFB4 K=4 on rolled long ctx + full-prefill wall
    WHEN deciding H-GPFB4-LONG
    THEN k=4 only; L_eff≫W; active≤W+S; dual gate; wall_roll≤wall_full+slack.
    """
    bad_k = require_k4(k)
    if bad_k is not None:
        return bad_k
    need = float(MIN_LEFF_RATIO) * float(w)
    if float(l_eff) < need:
        return (
            f"KILL (L_eff {float(l_eff):.0f} < {MIN_LEFF_RATIO:g}·W "
            f"={need:.0f})"
        )
    cap = float(w) + float(s)
    if float(mean_active) > cap + 1e-6:
        return (
            f"KILL (mean_active {float(mean_active):.0f} > W+S={cap:.0f})"
        )
    raw = decide_hgpfb4(
        parent_story=parent_story,
        parent_code=parent_code,
        gpfb4_story=long_story,
        gpfb4_code=long_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=k,
        identical=identical,
    )
    labeled = raw.replace("ABS-GPFB4 k=", "GPFB4-LONG k=", 1).replace(
        "GPFB4 never", "GPFB4-LONG never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    if float(wall_roll) > float(wall_full) + float(wall_slack_ms):
        return (
            f"KILL (wall_roll {float(wall_roll):.0f} > "
            f"wall_full+slack {float(wall_full) + float(wall_slack_ms):.0f})"
        )
    return labeled.replace(
        "code↑ story≥parent−ε)",
        (
            f"code↑ story≥parent−ε; L_eff={float(l_eff):.0f}≫W={int(w)}; "
            f"active={float(mean_active):.0f}≤W+S={int(w)+int(s)}; "
            f"wall_roll≤full+slack)"
        ),
        1,
    )
