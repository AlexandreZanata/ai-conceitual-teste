"""H-CUR2: n_stages ∈ {2,3,4,5} ablation vs H-CUR (n=3)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

CUR2_STAGES = (2, 3, 4, 5)
CUR2_CONTROL = 3

__all__ = [
    "CUR2_STAGES",
    "CUR2_CONTROL",
    "mean_lp_by_stages",
    "best_n_stages",
    "decide_hcur2",
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


def best_n_stages(lp_by_n: Mapping[int, float]) -> int:
    """Highest mean teacher_lp; ties prefer fewer stages."""
    if not lp_by_n:
        raise ValueError("best_n_stages: empty map")
    return max(lp_by_n, key=lambda n: (float(lp_by_n[n]), -int(n)))


def decide_hcur2(lp_by_n: Mapping[int, float]) -> str:
    """
    GIVEN mean teacher_lp per n_stages
    WHEN deciding H-CUR2 ablation
    THEN KILL if best ≤ H-CUR (n=3); else PROMOTE.
    """
    if CUR2_CONTROL not in lp_by_n:
        return "needs n_stages=3 (H-CUR) control"
    control = float(lp_by_n[CUR2_CONTROL])
    best = best_n_stages(lp_by_n)
    if float(lp_by_n[best]) <= control + 1e-6:
        return "KILL (best n ≤ H-CUR n=3)"
    return f"PROMOTE (best n_stages={best} > H-CUR)"
