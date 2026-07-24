"""H-CURL3: micro seq_lo grid {5,6,7} around tip lo=6."""

from __future__ import annotations

from typing import Mapping

from curl_ops import best_seq_lo, mean_lp_by_seq_lo

CURL3_LOS = (5, 6, 7)
CURL3_CONTROL = 6

__all__ = [
    "CURL3_LOS",
    "CURL3_CONTROL",
    "mean_lp_by_seq_lo",
    "best_seq_lo",
    "decide_hcurl3",
]


def decide_hcurl3(lp_by_lo: Mapping[int, float]) -> str:
    """
    GIVEN mean teacher_lp per seq_lo on micro grid
    WHEN deciding H-CURL3
    THEN KILL if best ≤ tip lo=6; else PROMOTE.
    """
    if CURL3_CONTROL not in lp_by_lo:
        return "needs seq_lo=6 (H-CURL2 tip) control"
    control = float(lp_by_lo[CURL3_CONTROL])
    best = best_seq_lo(lp_by_lo)
    if float(lp_by_lo[best]) <= control + 1e-6:
        return "KILL (best seq_lo ≤ H-CURL2 lo=6)"
    return f"PROMOTE (best seq_lo={best} > H-CURL2 tip)"
