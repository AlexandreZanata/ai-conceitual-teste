"""H-SUMCACHE: hierarchical summary+tail; wall < full-prefill PFB."""

from __future__ import annotations

from genc_ops import CHUNK_LENS, STRIDES
from pfb2_ops import K2_BEAMS
from pfb_ops import EPS_LP, MIN_UNIQUE, PFB_TEMP, decide_hpfb

__all__ = [
    "K2_BEAMS",
    "PFB_TEMP",
    "MIN_UNIQUE",
    "EPS_LP",
    "CHUNK_LENS",
    "STRIDES",
    "SUMCACHE_TARGET",
    "SUMCACHE_W",
    "SUMCACHE_S_COARSE",
    "SUMCACHE_S_FINE",
    "ACTIVE_CAP",
    "MIN_LEFF",
    "FULL_PREFILL_CAP",
    "WALL_SLACK_MS",
    "decide_hsumcache",
]

SUMCACHE_TARGET = 512
SUMCACHE_W = 256
SUMCACHE_S_COARSE = int(CHUNK_LENS[1])  # 64
SUMCACHE_S_FINE = int(CHUNK_LENS[0])  # 32 (GENC smoke scale)
ACTIVE_CAP = SUMCACHE_S_COARSE + SUMCACHE_S_FINE + SUMCACHE_W  # 352
MIN_LEFF = 512
# Full-prefill decode must leave room for max_new under pos=512.
FULL_PREFILL_CAP = 480
MAX_NEW_ROOM = 32
WALL_SLACK_MS = 5.0  # nano wall noise; still reject clear slowdowns


def decide_hsumcache(
    *,
    parent_story: float,
    parent_code: float,
    sum_story: float,
    sum_code: float,
    mean_unique: float,
    mean_elig: float,
    mean_switch: float,
    l_eff: float,
    mean_active: float,
    wall_sum: float,
    wall_full: float,
    identical: bool,
) -> str:
    """
    GIVEN EARLY vs PFB2 on summary+tail + full-prefill wall
    WHEN deciding H-SUMCACHE
    THEN L_eff≥512; active≤cap; dual gate; wall_sum < wall_full.
    """
    if float(l_eff) < float(MIN_LEFF):
        return f"KILL (L_eff {float(l_eff):.0f} < {MIN_LEFF})"
    if float(mean_active) > float(ACTIVE_CAP) + 1e-6:
        return (
            f"KILL (mean_active {float(mean_active):.0f} > "
            f"ACTIVE_CAP={ACTIVE_CAP})"
        )
    raw = decide_hpfb(
        parent_story=parent_story,
        parent_code=parent_code,
        pfb_story=sum_story,
        pfb_code=sum_code,
        mean_unique=mean_unique,
        mean_elig=mean_elig,
        mean_switch=mean_switch,
        k=K2_BEAMS,
        identical=identical,
    )
    labeled = raw.replace("ABS-PFB k=", "SUMCACHE k=", 1).replace(
        "PFB never", "SUMCACHE never", 1
    )
    if labeled.startswith("KILL"):
        return labeled
    if float(wall_sum) > float(wall_full) + float(WALL_SLACK_MS):
        return (
            f"KILL (wall_sum {float(wall_sum):.0f} > full-prefill "
            f"{float(wall_full):.0f}+slack={WALL_SLACK_MS:g})"
        )
    return labeled.replace(
        "code↑ story≥parent−ε)",
        (
            f"code↑ story≥parent−ε; L_eff={float(l_eff):.0f}; "
            f"active={float(mean_active):.0f}; "
            f"wall={float(wall_sum):.0f}≤full={float(wall_full):.0f}"
            f"+{WALL_SLACK_MS:g})"
        ),
        1,
    )
