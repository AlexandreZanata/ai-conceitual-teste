"""Wave AK4 H-FASTMORE: faster peak-extractive gen vs AJ FASTPEAK."""

from __future__ import annotations

import re
import time
from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from askfast_ops import WALL_DROP_MIN, wall_reduction
from asksmart_ops import is_period_collapse
from fastpeak_ops import AF_RAW_OPEN_WALL_MS
from fastplus_ops import mean_ms, ttft_of
from gentrue_ops import extract_gentrue_answer, gentrue_top_k_chunks
from genpeak_ops import normalize_gen_answer
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTMORE_ID",
    "FASTMORE_N",
    "AF_RAW_OPEN_WALL_MS",
    "FASTPEAK_HOT_WALL_MS",
    "FASTPEAK_WARM_WALL_MS",
    "FASTPEAK_COLD_WALL_MS",
    "FASTPEAK_HOT_E2E_MS",
    "MIN_GEN_MEAN",
    "WALL_DROP_MIN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "mean_ms",
    "ttft_of",
    "fastmore_generate",
    "score_fastmore_lookup",
    "score_fastmore_gen",
    "fastmore_stats",
    "decide_fastmore",
]

_WORD = re.compile(r"[a-z0-9]+", re.I)
# Tighter than FASTPEAK (_PEAK_K=6, _CTX_CAP=2400) for wall↓.
_PEAK_K = 4
_CTX_CAP = 1600

FASTMORE_ID = "H-FASTMORE"
FASTMORE_N = 10
MIN_GEN_MEAN = 5.0  # pesquisa §3 quality floor
# Published AJ4 FASTPEAK means (formal-hfastpeak-fastpeak.md).
FASTPEAK_COLD_WALL_MS = 5.3
FASTPEAK_WARM_WALL_MS = 5.0
FASTPEAK_HOT_WALL_MS = 5.0
FASTPEAK_HOT_E2E_MS = 50.0


def fastmore_generate(
    *,
    question: str,
    chunks: Sequence[str],
    k_retrieve: int = _PEAK_K,
) -> dict[str, Any]:
    """
    GIVEN question + source chunks (no gold, no student decode)
    WHEN peaking GENTRUE AK-aware span under wall clock
    THEN GENERATE payload with wall_ms>0 ∧ n_new>0 (peak-fast product).
    """
    t0 = time.perf_counter()
    hits = gentrue_top_k_chunks(question, chunks, max(1, int(k_retrieve)))
    ctx = "\n\n".join(hits)[:_CTX_CAP]
    peak = extract_gentrue_answer(question, ctx)
    text = normalize_gen_answer(str(peak or ""))
    if not text or is_period_collapse(text):
        fallback = hits[0][:80] if hits else "."
        text = normalize_gen_answer(fallback)
    wall_ms = (time.perf_counter() - t0) * 1000.0
    n_new = max(1, len(_WORD.findall(text)))
    return {
        "completion": text,
        "mode": "PEAK_FAST+GENTRUE",
        "wall_ms": float(wall_ms),
        "ttft_ms": float(wall_ms),
        "n_new": int(n_new),
        "peak_used": bool(peak),
        "cache_hit": False,
    }


def score_fastmore_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP quality only — NEVER claim LOOKUP wall=0 as speed IQ."""
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
        "FASTMORE LOOKUP product path — NOT speed IQ "
        "(vs H-FASTPEAK / LOOKUP-as-speed ban)",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_fastmore_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """GENERATE: wall_ms>0 ∧ n_new>0; score completion; peak ≠ open-chat."""
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
        f"FASTMORE gen vs H-FASTPEAK hot baseline "
        f"{FASTPEAK_HOT_WALL_MS:.3f} ms",
        "GENTRUE peak extractive — NOT open-chat IQ",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen wall_ms/n_new required"]
    return float(score), bool(err), notes


def fastmore_stats(
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
    GIVEN dual-arm FASTMORE timings
    WHEN summarizing AK4
    THEN gen wall>0 ∧ (warm|hot)↓ vs cold ∧ vs FASTPEAK + quality floor.
    """
    if len(lookup_scores) != FASTMORE_N or len(gen_scores) != FASTMORE_N:
        raise ValueError(f"FASTMORE requires {FASTMORE_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(FASTMORE_N))
    g_mean = float(sum(gen_scores) / float(FASTMORE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    drop_cold = wall_reduction(cold_wall_ms, hot_wall_ms)
    drop_vs_fp = wall_reduction(FASTPEAK_HOT_WALL_MS, hot_wall_ms)
    wall_down = float(warm_wall_ms) < float(cold_wall_ms) or (
        float(hot_wall_ms) < float(cold_wall_ms)
    )
    e2e_down = float(warm_e2e_ms) < float(cold_e2e_ms) or (
        float(hot_e2e_ms) < float(cold_e2e_ms)
    )
    ttft_down = float(warm_ttft_ms) < float(cold_ttft_ms) or (
        float(hot_ttft_ms) < float(cold_ttft_ms)
    )
    beats_fp_wall = float(hot_wall_ms) < float(FASTPEAK_HOT_WALL_MS) or (
        float(warm_wall_ms) < float(FASTPEAK_WARM_WALL_MS)
    )
    beats_fp_e2e = float(hot_e2e_ms) < float(FASTPEAK_HOT_E2E_MS)
    return {
        "n_trials": FASTMORE_N,
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
        "fastpeak_hot_wall_ms": float(FASTPEAK_HOT_WALL_MS),
        "fastpeak_warm_wall_ms": float(FASTPEAK_WARM_WALL_MS),
        "fastpeak_cold_wall_ms": float(FASTPEAK_COLD_WALL_MS),
        "fastpeak_hot_e2e_ms": float(FASTPEAK_HOT_E2E_MS),
        "wall_drop_vs_cold": float(drop_cold),
        "wall_drop_vs_fastpeak": float(drop_vs_fp),
        "wall_drop_min": float(WALL_DROP_MIN),
        "min_gen_mean": float(MIN_GEN_MEAN),
        "pass_gen_telemetry": int(n_gen_wall_ok) >= FASTMORE_N,
        "pass_speed": bool(wall_down or e2e_down or ttft_down),
        "pass_vs_fastpeak": bool(
            beats_fp_wall
            or beats_fp_e2e
            or float(drop_vs_fp) >= float(WALL_DROP_MIN)
        ),
        "pass_lookup_quality": l_mean >= PASS_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_quality_floor": g_mean >= MIN_GEN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_fastmore(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTMORE stats
    WHEN applying pesquisa §3 AK4 gate
    THEN KILL if false-hit or gen wall=0; PROMOTE if vs-FASTPEAK∧floor∧lookup;
         HOLD if soft-fail with numbers logged.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_gen_telemetry")):
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    ready = (
        bool(stats.get("pass_vs_fastpeak"))
        and bool(stats.get("pass_lookup_quality"))
        and bool(stats.get("pass_quality_floor"))
    )
    if ready:
        return "PROMOTE"
    return "HOLD"
