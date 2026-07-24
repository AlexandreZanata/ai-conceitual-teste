"""H-STAG: n_stages ∈ {2,3,4} under CURL2 seq_lo=6."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

from curl_ops import best_seq_lo

STAG_STAGES = (2, 3, 4)
STAG_CONTROL = 3
STAG_SEQ_LO = 6

__all__ = [
    "STAG_STAGES",
    "STAG_CONTROL",
    "STAG_SEQ_LO",
    "mean_lp_by_stages",
    "best_stages",
    "decide_hstag",
]


def mean_lp_by_stages(rows: Sequence[Mapping[str, Any]]) -> dict[int, float]:
    """
    GIVEN eval rows with n_stages + teacher_mean_logprob
    WHEN aggregating
    THEN return mean teacher_lp per n_stages.
    """
    buckets: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        buckets[int(r["n_stages"])].append(float(r["teacher_mean_logprob"]))
    return {k: sum(v) / len(v) for k, v in buckets.items()}


def best_stages(lp_by_st: Mapping[int, float]) -> int:
    """Highest mean teacher_lp; ties prefer smaller n_stages."""
    return best_seq_lo(lp_by_st)


def decide_hstag(lp_by_st: Mapping[int, float]) -> str:
    """
    GIVEN mean teacher_lp per n_stages
    WHEN deciding H-STAG
    THEN KILL if best ≤ tip stages=3; else PROMOTE.
    """
    if STAG_CONTROL not in lp_by_st:
        return "needs n_stages=3 (H-CURL2 tip) control"
    control = float(lp_by_st[STAG_CONTROL])
    best = best_stages(lp_by_st)
    if float(lp_by_st[best]) <= control + 1e-6:
        return "KILL (best n_stages ≤ H-CURL2 stages=3)"
    return f"PROMOTE (best n_stages={best} > H-CURL2 tip)"
