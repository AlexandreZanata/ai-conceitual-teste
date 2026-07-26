"""Wave AE3 H-FASTMAX: faster held-out ask vs recorded FASTPLUS baseline."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from askfast_ops import WALL_DROP_MIN, wall_reduction
from fastplus_ops import (
    AB_ASKFAST_E2E_MS,
    AB_ASKFAST_MEAN_WALL_MS,
    AB_OPEN_MEAN_WALL_MS,
    mean_ms,
    ttft_of,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTMAX_ID",
    "FASTMAX_N",
    "WALL_DROP_MIN",
    "FASTPLUS_WARM_E2E_MS",
    "FASTPLUS_COLD_E2E_MS",
    "FASTPLUS_WARM_WALL_MS",
    "AB_ASKFAST_E2E_MS",
    "AB_ASKFAST_MEAN_WALL_MS",
    "AB_OPEN_MEAN_WALL_MS",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "ttft_of",
    "mean_ms",
    "score_fastmax_trial",
    "fastmax_stats",
    "decide_fastmax",
]

FASTMAX_ID = "H-FASTMAX"
FASTMAX_N = 10
# Evidence: results/nano-lm/wave-ac/fastplus_summary.json
FASTPLUS_WARM_E2E_MS = 0.2903160002460936
FASTPLUS_COLD_E2E_MS = 1.0746810003183782
FASTPLUS_WARM_WALL_MS = 0.0


def score_fastmax_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN FASTMAX ask result
    WHEN scoring HITL
    THEN SEMWRAP known-ask bar + speed note.
    """
    from askfast_ops import score_askfast_trial

    score, err, notes = score_askfast_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    return score, err, list(notes) + [
        "FASTMAX: ASKFAST+cache+parallel-hot — not STREAM/open chat"
    ]


def fastmax_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    cold_wall_ms: float,
    warm_wall_ms: float,
    hot_wall_ms: float,
    cold_ttft_ms: float,
    warm_ttft_ms: float,
    hot_ttft_ms: float,
    cold_e2e_ms: float,
    warm_e2e_ms: float,
    hot_e2e_ms: float,
    cache_hit_rate: float,
) -> dict[str, Any]:
    """
    GIVEN 10 FASTMAX scores + timing vs FASTPLUS baselines
    WHEN summarizing AE3
    THEN quality + wall/TTFT/e2e↓ vs FASTPLUS (or HOLD path).
    """
    if len(scores) != FASTMAX_N or len(errors) != FASTMAX_N:
        raise ValueError(f"FASTMAX requires exactly {FASTMAX_N} scores/errors")
    mean = float(sum(scores) / float(FASTMAX_N))
    n_err = int(sum(1 for e in errors if e))
    drop_open = wall_reduction(AB_OPEN_MEAN_WALL_MS, cold_wall_ms)
    e2e_vs_fp = float(hot_e2e_ms) < float(FASTPLUS_WARM_E2E_MS) or (
        float(warm_e2e_ms) < float(FASTPLUS_WARM_E2E_MS)
    )
    wall_vs_fp = float(hot_wall_ms) < float(FASTPLUS_WARM_WALL_MS) or (
        float(warm_wall_ms) < float(FASTPLUS_WARM_WALL_MS)
    )
    ttft_vs_fp = float(hot_ttft_ms) < float(FASTPLUS_WARM_WALL_MS) or (
        float(warm_ttft_ms) < float(FASTPLUS_WARM_WALL_MS)
    )
    wall_drop_ok = drop_open >= float(WALL_DROP_MIN)
    e2e_vs_ab = float(hot_e2e_ms) < float(AB_ASKFAST_E2E_MS)
    return {
        "n_trials": FASTMAX_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "cold_wall_ms": float(cold_wall_ms),
        "warm_wall_ms": float(warm_wall_ms),
        "hot_wall_ms": float(hot_wall_ms),
        "cold_ttft_ms": float(cold_ttft_ms),
        "warm_ttft_ms": float(warm_ttft_ms),
        "hot_ttft_ms": float(hot_ttft_ms),
        "cold_e2e_ms": float(cold_e2e_ms),
        "warm_e2e_ms": float(warm_e2e_ms),
        "hot_e2e_ms": float(hot_e2e_ms),
        "cache_hit_rate": float(cache_hit_rate),
        "fastplus_warm_e2e_ms": float(FASTPLUS_WARM_E2E_MS),
        "fastplus_cold_e2e_ms": float(FASTPLUS_COLD_E2E_MS),
        "fastplus_warm_wall_ms": float(FASTPLUS_WARM_WALL_MS),
        "ab_askfast_e2e_ms": float(AB_ASKFAST_E2E_MS),
        "ab_open_mean_wall_ms": float(AB_OPEN_MEAN_WALL_MS),
        "wall_drop_vs_ab_open": float(drop_open),
        "wall_drop_min": float(WALL_DROP_MIN),
        "pass_e2e_vs_fastplus": bool(e2e_vs_fp),
        "pass_wall_vs_fastplus": bool(wall_vs_fp),
        "pass_ttft_vs_fastplus": bool(ttft_vs_fp),
        "pass_wall_drop": bool(wall_drop_ok),
        "pass_e2e_vs_ab": bool(e2e_vs_ab),
        # Beyond FASTPLUS: wall|TTFT|e2e must beat FASTPLUS (AB drop is report-only).
        "pass_speed": bool(e2e_vs_fp or wall_vs_fp or ttft_vs_fp),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_fastmax(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTMAX stats
    WHEN applying pesquisa §5 AE3 gate
    THEN PROMOTE if quality ∧ (wall|TTFT|e2e ↓ vs FASTPLUS/AB) ∧ no false-hit;
         HOLD if quality but speed soft-fail (numbers required);
         KILL if false-hit or quality fail.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_quality")):
        return "KILL"
    if bool(stats.get("pass_speed")):
        return "PROMOTE"
    return "HOLD"
