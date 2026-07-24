"""H-CURL2: fine seq_lo grid around tip lo=8."""

from __future__ import annotations

from typing import Mapping

from curl_ops import best_seq_lo, mean_lp_by_seq_lo

CURL2_LOS = (4, 6, 8, 10, 12)
CURL2_CONTROL = 8

__all__ = [
    "CURL2_LOS",
    "CURL2_CONTROL",
    "mean_lp_by_seq_lo",
    "best_seq_lo",
    "decide_hcurl2",
]


def decide_hcurl2(lp_by_lo: Mapping[int, float]) -> str:
    """
    GIVEN mean teacher_lp per seq_lo on fine grid
    WHEN deciding H-CURL2
    THEN KILL if best ≤ tip lo=8; else PROMOTE.
    """
    if CURL2_CONTROL not in lp_by_lo:
        return "needs seq_lo=8 (H-CURL tip) control"
    control = float(lp_by_lo[CURL2_CONTROL])
    best = best_seq_lo(lp_by_lo)
    if float(lp_by_lo[best]) <= control + 1e-6:
        return "KILL (best seq_lo ≤ H-CURL lo=8)"
    return f"PROMOTE (best seq_lo={best} > H-CURL tip)"
