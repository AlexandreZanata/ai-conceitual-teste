"""H-AMORT: amortized soft-cache e2e — build once, many PRE3 runs."""

from __future__ import annotations

from typing import Sequence

from lat_ops import EPS_LP

__all__ = [
    "EPS_LP",
    "DEFAULT_N_RUNS",
    "amortized_e2e",
    "decide_hamort",
]

# Runs sharing one cache; enough to beat formal ETRAIN cache tax (~0.64s).
DEFAULT_N_RUNS = 4


def amortized_e2e(cache_build_s: float, train_walls: Sequence[float]) -> float:
    """
    GIVEN one cache build and N PRE3 train walls
    WHEN amortizing
    THEN return cache/N + mean(train_wall).
    """
    n = len(train_walls)
    if n < 1:
        raise ValueError("amortized_e2e: need ≥1 train wall")
    if float(cache_build_s) < 0.0:
        raise ValueError("amortized_e2e: cache_build_s must be >= 0")
    mean_train = sum(float(w) for w in train_walls) / float(n)
    return float(cache_build_s) / float(n) + mean_train


def decide_hamort(
    *,
    amort_e2e: float,
    live_e2e: float,
    amort_lp: float,
    live_lp: float,
    n_runs: int,
    eps_lp: float = EPS_LP,
) -> str:
    """
    GIVEN amortized PRE3 e2e vs live STAG train wall
    WHEN deciding (new e2e story without ASYNC)
    THEN KILL if lp < STAG−ε or amort_e2e ≥ live; else PROMOTE.
    """
    if int(n_runs) < 1:
        return "KILL (n_runs < 1)"
    if float(amort_lp) < float(live_lp) - float(eps_lp):
        return "KILL (quality drop vs H-STAG)"
    if float(amort_e2e) >= float(live_e2e):
        return "KILL (amortized e2e ≥ live STAG)"
    return f"PROMOTE (amortized e2e over n={int(n_runs)} PRE3 runs)"
