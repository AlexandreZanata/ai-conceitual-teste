"""Wave AC3 H-FASTPLUS: faster held-out ask vs recorded AB ASKFAST baseline."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from askfast_ops import WALL_DROP_MIN, wall_reduction
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTPLUS_ID",
    "FASTPLUS_N",
    "WALL_DROP_MIN",
    "AB_ASKFAST_MEAN_WALL_MS",
    "AB_ASKFAST_E2E_MS",
    "AB_OPEN_MEAN_WALL_MS",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "ttft_of",
    "mean_ms",
    "score_fastplus_trial",
    "fastplus_stats",
    "decide_fastplus",
]

FASTPLUS_ID = "H-FASTPLUS"
FASTPLUS_N = 10
# Evidence: results/nano-lm/wave-ab/askfast_summary.json
AB_ASKFAST_MEAN_WALL_MS = 0.0
AB_ASKFAST_E2E_MS = 88.75692499987053
AB_OPEN_MEAN_WALL_MS = 25.17925870010913


def ttft_of(payload: Mapping[str, Any]) -> float:
    """
    GIVEN an ask payload
    WHEN reading first-token latency
    THEN use ttft_ms if present else wall_ms (wrap path ≈ TTFT).
    """
    if payload.get("ttft_ms") is not None:
        return float(payload["ttft_ms"])
    return float(payload.get("wall_ms") or 0.0)


def mean_ms(values: Sequence[float]) -> float:
    if not values:
        return 0.0
    return float(sum(float(v) for v in values) / float(len(values)))


def score_fastplus_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN FASTPLUS ask result
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
        "FASTPLUS: ASKFAST+cache on held-out — not STREAM/open chat"
    ]


def fastplus_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    cold_wall_ms: float,
    warm_wall_ms: float,
    cold_ttft_ms: float,
    warm_ttft_ms: float,
    cold_e2e_ms: float,
    warm_e2e_ms: float,
    cache_hit_rate: float,
) -> dict[str, Any]:
    """
    GIVEN 10 FASTPLUS scores + timing vs AB baselines
    WHEN summarizing AC3
    THEN quality + wall/TTFT/e2e pass flags.
    """
    if len(scores) != FASTPLUS_N or len(errors) != FASTPLUS_N:
        raise ValueError(f"FASTPLUS requires exactly {FASTPLUS_N} scores/errors")
    mean = float(sum(scores) / float(FASTPLUS_N))
    n_err = int(sum(1 for e in errors if e))
    drop_open = wall_reduction(AB_OPEN_MEAN_WALL_MS, cold_wall_ms)
    drop_ab_wall = wall_reduction(AB_ASKFAST_MEAN_WALL_MS, warm_wall_ms)
    # e2e↓: warm pack faster than recorded AB ASKFAST e2e
    e2e_down = float(warm_e2e_ms) < float(AB_ASKFAST_E2E_MS)
    ttft_down = float(warm_ttft_ms) < float(AB_ASKFAST_MEAN_WALL_MS) or (
        float(warm_ttft_ms) <= float(AB_ASKFAST_MEAN_WALL_MS)
        and float(cold_ttft_ms) < float(AB_OPEN_MEAN_WALL_MS)
    )
    wall_down = drop_open >= float(WALL_DROP_MIN) or float(warm_wall_ms) < float(
        AB_ASKFAST_MEAN_WALL_MS
    )
    return {
        "n_trials": FASTPLUS_N,
        "mean": mean,
        "n_errors": n_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "cold_wall_ms": float(cold_wall_ms),
        "warm_wall_ms": float(warm_wall_ms),
        "cold_ttft_ms": float(cold_ttft_ms),
        "warm_ttft_ms": float(warm_ttft_ms),
        "cold_e2e_ms": float(cold_e2e_ms),
        "warm_e2e_ms": float(warm_e2e_ms),
        "cache_hit_rate": float(cache_hit_rate),
        "ab_askfast_mean_wall_ms": float(AB_ASKFAST_MEAN_WALL_MS),
        "ab_askfast_e2e_ms": float(AB_ASKFAST_E2E_MS),
        "ab_open_mean_wall_ms": float(AB_OPEN_MEAN_WALL_MS),
        "wall_drop_vs_ab_open": float(drop_open),
        "wall_drop_vs_ab_askfast": float(drop_ab_wall),
        "wall_drop_min": float(WALL_DROP_MIN),
        "pass_wall": bool(wall_down),
        "pass_ttft": bool(ttft_down),
        "pass_e2e": bool(e2e_down),
        "pass_speed": bool(wall_down or ttft_down or e2e_down),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_fastplus(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTPLUS stats
    WHEN applying §8.5 / §12.1 AC3 gate
    THEN PROMOTE if quality ∧ speed↓ ∧ no false-hit;
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
