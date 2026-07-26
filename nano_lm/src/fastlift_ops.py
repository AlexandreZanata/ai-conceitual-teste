"""Wave AH4 H-FASTLIFT: faster generative ask (wall_ms>0) vs AG FASTREAL."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from askfast_ops import WALL_DROP_MIN, wall_reduction
from fastplus_ops import mean_ms, ttft_of
from fastreal_ops import AF_RAW_OPEN_WALL_MS, FASTREAL_ID
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTLIFT_ID",
    "FASTLIFT_N",
    "AF_RAW_OPEN_WALL_MS",
    "FASTREAL_HOT_WALL_MS",
    "FASTREAL_WARM_WALL_MS",
    "FASTREAL_COLD_WALL_MS",
    "FASTREAL_HOT_E2E_MS",
    "WALL_DROP_MIN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "mean_ms",
    "ttft_of",
    "score_fastlift_lookup",
    "score_fastlift_gen",
    "fastlift_stats",
    "decide_fastlift",
]

FASTLIFT_ID = "H-FASTLIFT"
FASTLIFT_N = 10
# Published AG4 FASTREAL means (formal-hfastreal-fastreal.md) — gen arm only.
FASTREAL_COLD_WALL_MS = 35.2
FASTREAL_WARM_WALL_MS = 16.3
FASTREAL_HOT_WALL_MS = 16.1
FASTREAL_HOT_E2E_MS = 1371.0


def score_fastlift_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN LOOKUP arm
    WHEN Cursor EVAL
    THEN quality score; notes forbid using LOOKUP as speed IQ.
    """
    from askfast_ops import score_askfast_trial

    score, err, notes = score_askfast_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        "FASTLIFT LOOKUP product path — NOT speed IQ "
        f"(vs {FASTREAL_ID} wall=0 claim ban)",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_fastlift_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm
    WHEN Cursor EVAL + telemetry check
    THEN require wall_ms>0 ∧ n_new>0; score completion honestly.
    """
    from antifp_ops import score_antifp_completion

    score, err, notes = score_antifp_completion(
        arm="GENERATE",
        completion=completion,
        gold=expected_gold,
    )
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        f"FASTLIFT gen vs {FASTREAL_ID} hot baseline "
        f"{FASTREAL_HOT_WALL_MS:.3f} ms",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen wall_ms/n_new required"]
    return float(score), bool(err), notes


def fastlift_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    cold_wall_ms: float,
    warm_wall_ms: float,
    hot_wall_ms: float,
    cold_ttft_ms: float,
    warm_ttft_ms: float,
    hot_ttft_ms: float,
    cold_e2e_ms: float,
    warm_e2e_ms: float,
    hot_e2e_ms: float,
    n_gen_wall_ok: int,
    n_fix: int,
) -> dict[str, Any]:
    """
    GIVEN dual-arm FASTLIFT timings
    WHEN summarizing AH4
    THEN gen wall_ms>0 ∧ (warm|hot)↓ vs cold ∧ vs FASTREAL hot.
    """
    if len(lookup_scores) != FASTLIFT_N or len(gen_scores) != FASTLIFT_N:
        raise ValueError(f"FASTLIFT requires {FASTLIFT_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(FASTLIFT_N))
    g_mean = float(sum(gen_scores) / float(FASTLIFT_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    drop_cold = wall_reduction(cold_wall_ms, hot_wall_ms)
    drop_vs_fr = wall_reduction(FASTREAL_HOT_WALL_MS, hot_wall_ms)
    wall_down = float(warm_wall_ms) < float(cold_wall_ms) or (
        float(hot_wall_ms) < float(cold_wall_ms)
    )
    e2e_down = float(warm_e2e_ms) < float(cold_e2e_ms) or (
        float(hot_e2e_ms) < float(cold_e2e_ms)
    )
    ttft_down = float(warm_ttft_ms) < float(cold_ttft_ms) or (
        float(hot_ttft_ms) < float(cold_ttft_ms)
    )
    beats_fr_wall = float(hot_wall_ms) < float(FASTREAL_HOT_WALL_MS) or (
        float(warm_wall_ms) < float(FASTREAL_WARM_WALL_MS)
    )
    beats_fr_e2e = float(hot_e2e_ms) < float(FASTREAL_HOT_E2E_MS)
    return {
        "n_trials": FASTLIFT_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_gen_wall_ok": int(n_gen_wall_ok),
        "n_fix": int(n_fix),
        "cold_wall_ms": float(cold_wall_ms),
        "warm_wall_ms": float(warm_wall_ms),
        "hot_wall_ms": float(hot_wall_ms),
        "cold_ttft_ms": float(cold_ttft_ms),
        "warm_ttft_ms": float(warm_ttft_ms),
        "hot_ttft_ms": float(hot_ttft_ms),
        "cold_e2e_ms": float(cold_e2e_ms),
        "warm_e2e_ms": float(warm_e2e_ms),
        "hot_e2e_ms": float(hot_e2e_ms),
        "af_raw_open_wall_ms": float(AF_RAW_OPEN_WALL_MS),
        "fastreal_hot_wall_ms": float(FASTREAL_HOT_WALL_MS),
        "fastreal_warm_wall_ms": float(FASTREAL_WARM_WALL_MS),
        "fastreal_cold_wall_ms": float(FASTREAL_COLD_WALL_MS),
        "fastreal_hot_e2e_ms": float(FASTREAL_HOT_E2E_MS),
        "wall_drop_vs_cold": float(drop_cold),
        "wall_drop_vs_fastreal": float(drop_vs_fr),
        "wall_drop_min": float(WALL_DROP_MIN),
        "pass_gen_telemetry": int(n_gen_wall_ok) >= FASTLIFT_N,
        "pass_speed": bool(wall_down or e2e_down or ttft_down),
        "pass_vs_fastreal": bool(
            beats_fr_wall
            or beats_fr_e2e
            or float(drop_vs_fr) >= float(WALL_DROP_MIN)
        ),
        "pass_lookup_quality": l_mean >= PASS_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_fastlift(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTLIFT stats
    WHEN applying pesquisa §5 AH4 gate
    THEN KILL if false-hit or gen wall=0; PROMOTE if vs-FASTREAL∧telemetry;
         HOLD if soft-fail with numbers logged.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_gen_telemetry")):
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    # AH4: must beat AG FASTREAL gen baseline (not merely warm vs cold).
    if bool(stats.get("pass_vs_fastreal")) and bool(
        stats.get("pass_lookup_quality")
    ):
        return "PROMOTE"
    return "HOLD"
