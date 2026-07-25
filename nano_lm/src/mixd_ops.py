"""H-MIXD: STAG curriculum + curated programming mix — dual gate."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "EPS_LP",
    "MIX_FRAC",
    "TRAIN_DOMAIN",
    "decide_hmixd",
]

MIX_FRAC = 0.1
TRAIN_DOMAIN = "programming"


def decide_hmixd(
    *,
    mix_story_lp: float,
    ctrl_story_lp: float,
    mix_prog_ppl: float,
    ctrl_prog_ppl: float,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN mix vs story-only control story teacher_lp and prog PPL
    WHEN deciding domain-mix capacity
    THEN PROMOTE iff story ≥ control−ε and prog PPL strictly down.
    """
    if float(mix_story_lp) < float(ctrl_story_lp) - float(eps_lp):
        return (
            f"KILL (story teacher_lp regress vs STAG control: "
            f"{mix_story_lp:.4f} < {ctrl_story_lp:.4f}−{eps_lp})"
        )
    if not (float(mix_prog_ppl) < float(ctrl_prog_ppl)):
        return (
            f"KILL (prog PPL not improved: "
            f"{mix_prog_ppl:.4f} ≥ {ctrl_prog_ppl:.4f})"
        )
    return (
        "PROMOTE (story ≥ STAG−ε and prog PPL ↓ vs story-only; "
        f"mix_frac={MIX_FRAC})"
    )
