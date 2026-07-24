"""H-SYS: CURL train tip × EARLY|POOL decode; free-lunch gate."""

from __future__ import annotations

from typing import Mapping

from cur_ops import N_STAGES

__all__ = [
    "SYS_SEQ_LO",
    "SYS_STAGES",
    "SYS_EARLY",
    "SYS_POOL",
    "decide_hsys_arm",
    "decide_hsys",
]

SYS_SEQ_LO = 8
SYS_STAGES = N_STAGES
SYS_EARLY = "H-SYS-E"
SYS_POOL = "H-SYS-P"


def decide_hsys_arm(
    s: Mapping[str, float],
    stats: Mapping[str, Mapping[str, float]],
    *,
    tip_family: str,
) -> str:
    """
    GIVEN a SYS arm vs H-CURL default-decode and tip@B2
    WHEN deciding
    THEN PROMOTE iff lp > CURL and lp > tip@B2; else KILL (free lunch).
    """
    curl = stats.get("H-CURL")
    tip = stats.get(tip_family)
    if curl is None or tip is None:
        return f"needs H-CURL+{tip_family}"
    if float(s["mean_lp"]) <= float(curl["mean_lp"]) + 1e-6:
        return "KILL (≤ CURL default decode)"
    if float(s["mean_lp"]) <= float(tip["mean_lp"]) + 1e-6:
        return f"KILL (≤ {tip_family}@B2)"
    return f"PROMOTE (beats CURL + {tip_family}@B2)"


def decide_hsys(stats: Mapping[str, Mapping[str, float]]) -> str:
    """
    GIVEN H-SYS-E / H-SYS-P arms plus controls
    WHEN deciding
    THEN PROMOTE if any arm clears free-lunch gate; else KILL.
    """
    arms = (
        (SYS_EARLY, "H-EARLY"),
        (SYS_POOL, "H-POOL"),
    )
    decisions: list[str] = []
    for fam, tip in arms:
        row = stats.get(fam)
        if row is None:
            continue
        d = decide_hsys_arm(row, stats, tip_family=tip)
        if d.startswith("PROMOTE"):
            return f"PROMOTE ({fam}: {d})"
        decisions.append(f"{fam}: {d}")
    if not decisions:
        return "needs H-SYS-E or H-SYS-P rows"
    return "KILL (" + "; ".join(decisions) + ")"
