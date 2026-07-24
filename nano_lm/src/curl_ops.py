"""H-CURL: seq_lo ∈ {8,16,32} ablation vs H-CUR (seq_lo=16)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from cur_ops import DEFAULT_SEQ_LO

CURL_LOS = (8, 16, 32)
CURL_CONTROL = DEFAULT_SEQ_LO

__all__ = [
    "CURL_LOS",
    "CURL_CONTROL",
    "mean_lp_by_seq_lo",
    "best_seq_lo",
    "decide_hcurl",
]


def mean_lp_by_seq_lo(rows: Sequence[Mapping[str, Any]]) -> dict[int, float]:
    """
    GIVEN eval rows with seq_lo + teacher_mean_logprob
    WHEN aggregating
    THEN return mean teacher_lp per seq_lo.
    """
    buckets: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        buckets[int(r["seq_lo"])].append(float(r["teacher_mean_logprob"]))
    return {k: sum(v) / len(v) for k, v in buckets.items()}


def best_seq_lo(lp_by_lo: Mapping[int, float]) -> int:
    """Highest mean teacher_lp; ties prefer smaller seq_lo."""
    if not lp_by_lo:
        raise ValueError("best_seq_lo: empty map")
    return max(lp_by_lo, key=lambda lo: (float(lp_by_lo[lo]), -int(lo)))


def decide_hcurl(lp_by_lo: Mapping[int, float]) -> str:
    """
    GIVEN mean teacher_lp per seq_lo
    WHEN deciding H-CURL ablation
    THEN KILL if best ≤ H-CUR (seq_lo=16); else PROMOTE.
    """
    if CURL_CONTROL not in lp_by_lo:
        return "needs seq_lo=16 (H-CUR) control"
    control = float(lp_by_lo[CURL_CONTROL])
    best = best_seq_lo(lp_by_lo)
    if float(lp_by_lo[best]) <= control + 1e-6:
        return "KILL (best seq_lo ≤ H-CUR lo=16)"
    return f"PROMOTE (best seq_lo={best} > H-CUR)"
