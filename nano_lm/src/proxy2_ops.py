"""H-PROXY2: teacher-forced CE proxy vs H-DECK self-lp @ equal forwards."""

from __future__ import annotations

from typing import Mapping

__all__ = ["decide_hproxy2"]


def decide_hproxy2(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-PROXY2 stats vs H-DECK
    WHEN deciding
    THEN KILL if quality ≤ H-DECK or more teacher forwards; else PROMOTE.
    """
    hdeck = stats.get("H-DECK")
    if hdeck is None:
        return "needs H-DECK control"
    if float(s["mean_lp"]) <= float(hdeck["mean_lp"]) + 1e-6:
        return "KILL (≤ H-DECK quality@forwards)"
    hyp_fwd = float(s.get("teacher_forwards", 0.0))
    ctl_fwd = float(hdeck.get("teacher_forwards", 0.0))
    if hyp_fwd > ctl_fwd + 1e-6:
        return "KILL (more teacher forwards than H-DECK)"
    return "PROMOTE (quality@forwards vs H-DECK)"
