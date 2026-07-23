"""H-DECP: per-prompt gene bank; claim picks gene by student proxy."""

from __future__ import annotations

from typing import Mapping, Sequence

__all__ = ["best_index", "decide_hdecp"]


def best_index(scores: Sequence[float]) -> int:
    """
    GIVEN non-empty scores
    WHEN selecting
    THEN return index of the maximum (stable on ties: lowest index).
    """
    if not scores:
        raise ValueError("best_index: empty scores")
    best_i, best_v = 0, float(scores[0])
    for i, v in enumerate(scores):
        if float(v) > best_v:
            best_i, best_v = i, float(v)
    return best_i


def decide_hdecp(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DECP vs B4 and GLOBAL (single gene on all fit prompts)
    WHEN deciding
    THEN PROMOTE only if lp > B4 and lp > GLOBAL; else KILL.
    """
    b4 = stats.get("B4")
    glo = stats.get("GLOBAL")
    if b4 is None:
        return "needs B4 control"
    if glo is None:
        return "needs GLOBAL control"
    s_lp = float(s["mean_lp"])
    if s_lp <= float(b4["mean_lp"]):
        return "KILL (≤ B4)"
    if s_lp <= float(glo["mean_lp"]):
        return "KILL (≤ global gene)"
    return "PROMOTE (per-prompt bank > global and B4)"
