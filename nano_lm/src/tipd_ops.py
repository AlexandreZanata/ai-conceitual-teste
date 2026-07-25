"""H-TIPD: binary tip decision — RETIP becomes STAG′ xor stays util."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP
from retip_ops import capacity_win

__all__ = [
    "EPS_LP",
    "capacity_win",
    "serve_regresses",
    "decide_htipd",
    "tip_outcome",
]


def serve_regresses(
    retip: Mapping[str, float],
    control: Mapping[str, float],
    *,
    eps_lp: float = EPS_LP,
) -> bool:
    """
    GIVEN frozen tip-gene scores on STAG′ vs live STAG ckpts
    WHEN testing serve regression
    THEN True iff STAG′ lp drops below control − ε.
    """
    return float(retip["mean_lp"]) < float(control["mean_lp"]) - float(eps_lp)


def decide_htipd(
    *,
    retip_lp: float,
    control_lp: float,
    early_retip: Mapping[str, float] | None,
    early_control: Mapping[str, float] | None,
    pool_retip: Mapping[str, float] | None,
    pool_control: Mapping[str, float] | None,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN RETIP (STAG′) AR tip vs live STAG + frozen EARLY/POOL serve
    WHEN deciding tip replacement
    THEN PROMOTE iff STAG′ > STAG and neither EARLY nor POOL serve regresses;
         else KILL (keep H-STAG tip; RETIP stays util).
    """
    if not capacity_win(retip_lp, control_lp):
        return "KILL (keep H-STAG tip; STAG′ ≤ STAG on tip lp)"
    if early_retip is None or early_control is None:
        return "needs EARLY serve rows"
    if pool_retip is None or pool_control is None:
        return "needs POOL serve rows"
    if serve_regresses(early_retip, early_control, eps_lp=eps_lp):
        return "KILL (keep H-STAG tip; EARLY serve regresses)"
    if serve_regresses(pool_retip, pool_control, eps_lp=eps_lp):
        return "KILL (keep H-STAG tip; POOL serve regresses)"
    return "PROMOTE (STAG′ replaces H-STAG tip; capacity + serve holds)"


def tip_outcome(decision: str) -> str:
    """Map decide_htipd string to STAG_PRIME or UTIL."""
    if str(decision).startswith("PROMOTE"):
        return "STAG_PRIME"
    return "UTIL"
