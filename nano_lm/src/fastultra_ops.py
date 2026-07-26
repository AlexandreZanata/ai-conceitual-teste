"""Wave AF3 H-FASTULTRA: faster held-out ask vs recorded FASTMAX baseline."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from askfast_ops import WALL_DROP_MIN, wall_reduction
from fastmax_ops import FASTPLUS_WARM_E2E_MS, FASTPLUS_WARM_WALL_MS
from fastplus_ops import (
    AB_ASKFAST_E2E_MS,
    AB_ASKFAST_MEAN_WALL_MS,
    AB_OPEN_MEAN_WALL_MS,
    mean_ms,
    ttft_of,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTULTRA_ID",
    "FASTULTRA_N",
    "HOT_ROUNDS",
    "WARMUP_ROUNDS",
    "WALL_DROP_MIN",
    "FASTMAX_HOT_E2E_MS",
    "FASTMAX_WARM_E2E_MS",
    "FASTPLUS_WARM_E2E_MS",
    "FASTPLUS_WARM_WALL_MS",
    "AB_ASKFAST_E2E_MS",
    "AB_ASKFAST_MEAN_WALL_MS",
    "AB_OPEN_MEAN_WALL_MS",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "ttft_of",
    "mean_ms",
    "score_fastultra_trial",
    "fastultra_stats",
    "decide_fastultra",
]

FASTULTRA_ID = "H-FASTULTRA"
FASTULTRA_N = 10
# Deeper hot search than FASTMAX rounds=12.
HOT_ROUNDS = 48
WARMUP_ROUNDS = 8
# Evidence: results/nano-lm/wave-ae/fastmax_summary.json
FASTMAX_HOT_E2E_MS = 0.034374999813735485
FASTMAX_WARM_E2E_MS = 0.49394100096833427


def score_fastultra_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN FASTULTRA ask result
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
        "FASTULTRA: ASKFAST+key-peek+hot — not STREAM/open chat"
    ]


def fastultra_stats(
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
    GIVEN 10 FASTULTRA scores + timing vs FASTMAX baselines
    WHEN summarizing AF3
    THEN quality + wall/TTFT/e2e↓ vs FASTMAX (or HOLD path).
    """
    if len(scores) != FASTULTRA_N or len(errors) != FASTULTRA_N:
        raise ValueError(
            f"FASTULTRA requires exactly {FASTULTRA_N} scores/errors"
        )
    mean = float(sum(scores) / float(FASTULTRA_N))
    n_err = int(sum(1 for e in errors if e))
    drop_open = wall_reduction(AB_OPEN_MEAN_WALL_MS, cold_wall_ms)
    e2e_vs_fm = float(hot_e2e_ms) < float(FASTMAX_HOT_E2E_MS) or (
        float(warm_e2e_ms) < float(FASTMAX_WARM_E2E_MS)
    )
    wall_vs_fm = float(hot_wall_ms) < float(FASTPLUS_WARM_WALL_MS) or (
        float(warm_wall_ms) < float(FASTPLUS_WARM_WALL_MS)
    )
    ttft_vs_fm = float(hot_ttft_ms) < float(FASTPLUS_WARM_WALL_MS) or (
        float(warm_ttft_ms) < float(FASTPLUS_WARM_WALL_MS)
    )
    wall_drop_ok = drop_open >= float(WALL_DROP_MIN)
    e2e_vs_fp = float(hot_e2e_ms) < float(FASTPLUS_WARM_E2E_MS)
    return {
        "n_trials": FASTULTRA_N,
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
        "fastmax_hot_e2e_ms": float(FASTMAX_HOT_E2E_MS),
        "fastmax_warm_e2e_ms": float(FASTMAX_WARM_E2E_MS),
        "fastplus_warm_e2e_ms": float(FASTPLUS_WARM_E2E_MS),
        "ab_askfast_e2e_ms": float(AB_ASKFAST_E2E_MS),
        "ab_open_mean_wall_ms": float(AB_OPEN_MEAN_WALL_MS),
        "wall_drop_vs_ab_open": float(drop_open),
        "wall_drop_min": float(WALL_DROP_MIN),
        "pass_e2e_vs_fastmax": bool(e2e_vs_fm),
        "pass_wall_vs_fastmax": bool(wall_vs_fm),
        "pass_ttft_vs_fastmax": bool(ttft_vs_fm),
        "pass_e2e_vs_fastplus": bool(e2e_vs_fp),
        "pass_wall_drop": bool(wall_drop_ok),
        # Beyond FASTMAX: wall|TTFT|e2e must beat FASTMAX (HOLD if soft-fail).
        "pass_speed": bool(e2e_vs_fm or wall_vs_fm or ttft_vs_fm),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "hot_rounds": HOT_ROUNDS,
        "warmup_rounds": WARMUP_ROUNDS,
    }


def decide_fastultra(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTULTRA stats
    WHEN applying pesquisa §5 AF3 gate
    THEN PROMOTE if quality ∧ (wall|TTFT|e2e ↓ vs FASTMAX) ∧ no false-hit;
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
