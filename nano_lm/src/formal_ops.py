"""Formal claim helpers: mean-by-family and promote/kill vs B2."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence


def means_by_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, float]]:
    """
    GIVEN formal eval rows with family + teacher_mean_logprob
    WHEN aggregating
    THEN return mean lp/wall and n per family.
    """
    buckets: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[str(r["family"])].append(r)
    out: dict[str, dict[str, float]] = {}
    for fam, items in buckets.items():
        lps = [float(x["teacher_mean_logprob"]) for x in items]
        walls = [float(x.get("mean_wall_ms", float("nan"))) for x in items]
        out[fam] = {
            "lp": sum(lps) / len(lps),
            "wall": sum(walls) / len(walls),
            "n": float(len(items)),
            "overfit": 1.0 if any(bool(x.get("overfit")) for x in items) else 0.0,
            "collapsed": 1.0
            if any(
                bool(x.get("diversity_collapsed") or x.get("heads_collapsed"))
                for x in items
            )
            else 0.0,
        }
    return out


def decide_formal_vs_b2(
    hyp: str, stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN formal stats for hyp and B2
    WHEN deciding claim
    THEN KILL on collapse/overfit or ≤ B2; else PROMOTE confirmed.
    """
    if hyp not in stats:
        return f"needs {hyp} rows"
    if "B2" not in stats:
        return "needs B2 control"
    if float(stats[hyp].get("collapsed", 0.0)) > 0.0:
        return f"KILL (collapse; {hyp})"
    if float(stats[hyp].get("overfit", 0.0)) > 0.0:
        return f"KILL (overfit; {hyp})"
    delta = float(stats[hyp]["lp"]) - float(stats["B2"]["lp"])
    if delta > 0.0:
        return f"PROMOTE confirmed ({hyp} > B2)"
    return f"KILL / reverse smoke ({hyp} ≤ B2)"
