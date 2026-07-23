"""H-CASC: 3-stage cascade — proxy → mid teacher → full teacher."""

from __future__ import annotations

from typing import Mapping

from lofi_ops import wall_saved

__all__ = [
    "cascade_forward_budget",
    "decide_hcasc",
    "wall_saved",
]


def cascade_forward_budget(
    *,
    pop_size: int,
    generations: int,
    n_prompts: int,
    mid_k: int,
    final_k: int,
) -> tuple[int, int]:
    """
    GIVEN cascade widths
    WHEN counting teacher completion scores
    THEN return (cascade_forwards, full_hdec_forwards).
    """
    if min(pop_size, generations, n_prompts, mid_k, final_k) < 1:
        raise ValueError("cascade_forward_budget: all args must be >= 1")
    mk = min(mid_k, pop_size)
    fk = min(final_k, pop_size)
    casc = generations * (mk + fk) * n_prompts
    full = generations * pop_size * n_prompts
    return casc, full


def decide_hcasc(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-CASC stats vs B4
    WHEN deciding
    THEN KILL if no teacher-forward save or ≤ B4; else PROMOTE.
    """
    b4 = stats.get("B4")
    if b4 is None:
        return "needs B4 control"
    if float(s.get("wall_save", 0.0)) <= 0.0:
        return "KILL (no teacher-forward save)"
    if float(s["mean_lp"]) <= float(b4["mean_lp"]) + 1e-6:
        return "KILL (≤ B4)"
    return "PROMOTE (beats B4 @ forward save)"
