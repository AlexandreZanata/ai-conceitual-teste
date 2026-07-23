"""H-DECK2: top_k ∈ {1,2,3} ablation vs H-DECK (k=2)."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence

DECK2_TOP_KS = (1, 2, 3)


def mean_lp_by_top_k(rows: Sequence[Mapping[str, Any]]) -> dict[int, float]:
    """
    GIVEN eval rows with top_k + teacher_mean_logprob
    WHEN aggregating
    THEN return mean teacher_lp per top_k.
    """
    buckets: dict[int, list[float]] = defaultdict(list)
    for r in rows:
        buckets[int(r["top_k"])].append(float(r["teacher_mean_logprob"]))
    return {k: sum(v) / len(v) for k, v in buckets.items()}


def best_top_k(lp_by_k: Mapping[int, float]) -> int:
    """Return top_k with highest mean teacher_lp (ties prefer smaller k)."""
    if not lp_by_k:
        raise ValueError("best_top_k: empty map")
    return max(lp_by_k, key=lambda k: (float(lp_by_k[k]), -int(k)))


def decide_hdeck2(lp_by_k: Mapping[int, float]) -> str:
    """
    GIVEN mean teacher_lp per top_k
    WHEN deciding H-DECK2 ablation
    THEN KILL if best_k ≤ H-DECK (k=2); else PROMOTE.
    """
    if 2 not in lp_by_k:
        return "needs top_k=2 (H-DECK) control"
    control = float(lp_by_k[2])
    best_k = best_top_k(lp_by_k)
    if float(lp_by_k[best_k]) <= control + 1e-6:
        return "KILL (best k ≤ H-DECK k=2)"
    return f"PROMOTE (best top_k={best_k} > H-DECK)"
