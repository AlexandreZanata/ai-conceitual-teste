"""H-DECK decisions: cheap proxy rank + teacher top-k vs H-DEC."""

from __future__ import annotations

from typing import Mapping

from lofi_ops import EPS_LP, teacher_forward_budget, wall_saved

# Re-export for callers.
__all__ = [
    "teacher_forward_budget",
    "wall_saved",
    "decide_hdeck",
]


def decide_hdeck(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DECK stats vs H-DEC
    WHEN deciding
    THEN KILL if quality < H-DEC−ε or no teacher-forward save; else PROMOTE.
    """
    hdec = stats.get("H-DEC")
    if hdec is None:
        return "needs H-DEC control"
    if float(s["mean_lp"]) < float(hdec["mean_lp"]) - EPS_LP:
        return "KILL (worse quality than H-DEC)"
    if float(s.get("wall_save", 0.0)) <= 0.0:
        return "KILL (no teacher-forward save)"
    return "PROMOTE (quality@budget vs H-DEC)"
