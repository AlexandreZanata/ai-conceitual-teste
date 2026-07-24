"""H-CURT: adopted formal tip (n_stages=5, seq_lo=8); decide vs H-CUR."""

from __future__ import annotations

from typing import Mapping

__all__ = ["CURT_STAGES", "CURT_SEQ_LO", "decide_hcurt"]

CURT_STAGES = 5
CURT_SEQ_LO = 8


def decide_hcurt(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-CURT vs H-CUR
    WHEN deciding
    THEN PROMOTE iff teacher_lp > H-CUR; else KILL.
    """
    tip = stats.get("H-CUR")
    if tip is None:
        return "needs H-CUR control"
    if float(s["mean_lp"]) > float(tip["mean_lp"]) + 1e-6:
        return "PROMOTE (beats H-CUR tip)"
    return "KILL (≤ H-CUR tip)"
