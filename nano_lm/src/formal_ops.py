"""Formal claim helpers: mean-by-family and promote/kill vs B2."""

from __future__ import annotations

from collections import defaultdict
from typing import Any, Mapping, Sequence


def _flag(items: Sequence[Mapping[str, Any]], *keys: str) -> float:
    for x in items:
        if any(bool(x.get(k)) for k in keys):
            return 1.0
    return 0.0


def _family_means(items: Sequence[Mapping[str, Any]]) -> dict[str, float]:
    lps = [float(x["teacher_mean_logprob"]) for x in items]
    walls = [float(x.get("mean_wall_ms", float("nan"))) for x in items]
    return {
        "lp": sum(lps) / len(lps),
        "wall": sum(walls) / len(walls),
        "n": float(len(items)),
        "overfit": _flag(items, "overfit"),
        "collapsed": _flag(items, "diversity_collapsed", "heads_collapsed"),
        "unstable": _flag(items, "unstable"),
    }


def means_by_family(rows: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, float]]:
    """
    GIVEN formal eval rows with family + teacher_mean_logprob
    WHEN aggregating
    THEN return mean lp/wall and n per family.
    """
    buckets: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
    for r in rows:
        buckets[str(r["family"])].append(r)
    return {fam: _family_means(items) for fam, items in buckets.items()}


def decide_formal_vs_control(
    hyp: str, control: str, stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN formal stats for hyp and named control
    WHEN deciding claim
    THEN KILL on collapse/overfit/unstable or ≤ control; else PROMOTE.
    """
    if hyp not in stats:
        return f"needs {hyp} rows"
    if control not in stats:
        return f"needs {control} control"
    if float(stats[hyp].get("collapsed", 0.0)) > 0.0:
        return f"KILL (collapse; {hyp})"
    if float(stats[hyp].get("overfit", 0.0)) > 0.0:
        return f"KILL (overfit; {hyp})"
    if float(stats[hyp].get("unstable", 0.0)) > 0.0:
        return f"KILL (unstable; {hyp})"
    delta = float(stats[hyp]["lp"]) - float(stats[control]["lp"])
    if delta > 0.0:
        return f"PROMOTE confirmed ({hyp} > {control})"
    return f"KILL / reverse smoke ({hyp} ≤ {control})"


def decide_formal_vs_b2(
    hyp: str, stats: Mapping[str, Mapping[str, float]]
) -> str:
    """Claim gate vs B2 (wrapper)."""
    return decide_formal_vs_control(hyp, "B2", stats)
