"""H-RETIP: TPACK/PRE3 train → capacity vs live STAG + frozen EARLY/POOL serve."""

from __future__ import annotations

from typing import Mapping

from lat_ops import EPS_LP

__all__ = [
    "EPS_LP",
    "capacity_win",
    "serve_win",
    "decide_hretip",
]


def capacity_win(
    retip_lp: float,
    control_lp: float,
) -> bool:
    """
    GIVEN retip (PRE3) AR tip lp vs live STAG control
    WHEN testing capacity
    THEN True iff retip strictly beats control tip lp.
    """
    return float(retip_lp) > float(control_lp) + 1e-6


def serve_win(
    retip: Mapping[str, float],
    control: Mapping[str, float],
    *,
    eps_lp: float = EPS_LP,
) -> bool:
    """
    GIVEN frozen tip-gene scores on retip vs control ckpts
    WHEN testing serve transfer of train capacity
    THEN True iff lp ≥ control−ε and (wall < control or lp > control).
    """
    if float(retip["mean_lp"]) < float(control["mean_lp"]) - float(eps_lp):
        return False
    wall_win = float(retip["mean_wall"]) < float(control["mean_wall"])
    lp_win = float(retip["mean_lp"]) > float(control["mean_lp"]) + 1e-6
    return bool(wall_win or lp_win)


def decide_hretip(
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
    GIVEN PRE3 AR tip vs live STAG + frozen EARLY/POOL serve scores
    WHEN deciding
    THEN KILL iff tip_lp ≤ control AND no serve win; else PROMOTE.
    """
    cap = capacity_win(retip_lp, control_lp)
    early_ok = False
    pool_ok = False
    if early_retip is not None and early_control is not None:
        early_ok = serve_win(early_retip, early_control, eps_lp=eps_lp)
    if pool_retip is not None and pool_control is not None:
        pool_ok = serve_win(pool_retip, pool_control, eps_lp=eps_lp)
    if cap or early_ok or pool_ok:
        bits: list[str] = []
        if cap:
            bits.append("capacity")
        if early_ok:
            bits.append("EARLY-serve")
        if pool_ok:
            bits.append("POOL-serve")
        return f"PROMOTE ({'+'.join(bits)} win)"
    return "KILL (tip lp ≤ STAG control and no serve win)"
