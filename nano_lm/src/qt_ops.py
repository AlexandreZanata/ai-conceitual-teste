"""H-QT: int8 weight-only quantized PACK/EARLY serve."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from tchr_ops import lp_finite

__all__ = [
    "QT_BITS",
    "EPS_LP",
    "decide_hqt",
]

QT_BITS = 8


def decide_hqt(
    *,
    parent: Mapping[str, float],
    qt: Mapping[str, float],
    n_rows: int,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN fp EARLY parent vs int8-weight EARLY on prog@128
    WHEN deciding quantized PACK serve
    THEN PROMOTE iff n≥1, qt story_lp ≥ parent−ε, and (wall↓ or weight_bytes↓);
         else KILL.
    """
    if int(n_rows) < 1:
        return "KILL (no scored rows)"
    p_lp = float(parent.get("mean_story_lp", float("-inf")))
    q_lp = float(qt.get("mean_story_lp", float("-inf")))
    p_wall = float(parent.get("mean_wall_ms", float("nan")))
    q_wall = float(qt.get("mean_wall_ms", float("nan")))
    p_bytes = float(parent.get("weight_bytes", float("nan")))
    q_bytes = float(qt.get("weight_bytes", float("nan")))
    if not lp_finite(p_lp) or not lp_finite(q_lp):
        return "KILL (story teacher_lp not finite)"
    if q_lp < p_lp - float(eps_lp):
        return f"KILL (lp {q_lp:.4f} < PACK/EARLY−ε {p_lp - eps_lp:.4f})"
    wall_win = q_wall < p_wall
    mem_win = q_bytes < p_bytes
    if not (wall_win or mem_win):
        return "KILL (no wall↓ and no weight_bytes↓ vs parent)"
    wins = []
    if wall_win:
        wins.append("wall↓")
    if mem_win:
        wins.append("mem↓")
    return (
        "PROMOTE (int8 weight-only serve; lp ≥ parent−ε; "
        + "+".join(wins)
        + ")"
    )
