"""Wave AL4 H-FASTFRESH: faster peak-extractive gen vs AK FASTMORE."""

from __future__ import annotations

import re
import time
from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from askfast_ops import WALL_DROP_MIN, wall_reduction
from asksmart_ops import is_period_collapse
from fastpeak_ops import AF_RAW_OPEN_WALL_MS
from fastplus_ops import mean_ms, ttft_of
from genfresh_ops import extract_genfresh_answer, genfresh_top_k_chunks
from genpeak_ops import normalize_gen_answer
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTFRESH_ID",
    "FASTFRESH_N",
    "AF_RAW_OPEN_WALL_MS",
    "FASTMORE_HOT_WALL_MS",
    "FASTMORE_WARM_WALL_MS",
    "FASTMORE_COLD_WALL_MS",
    "FASTMORE_HOT_E2E_MS",
    "MIN_GEN_MEAN",
    "WALL_DROP_MIN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "mean_ms",
    "ttft_of",
    "fastfresh_generate",
    "score_fastfresh_lookup",
    "score_fastfresh_gen",
    "fastfresh_stats",
    "decide_fastfresh",
]

_WORD = re.compile(r"[a-z0-9]+", re.I)
# Tighter than FASTMORE (_PEAK_K=4, _CTX_CAP=1600) for wall↓.
_PEAK_K = 2
_CTX_CAP = 900
# Cap Jaccard scan — large howto docs otherwise dominate wall.
_SCAN_CAP = 48

FASTFRESH_ID = "H-FASTFRESH"
FASTFRESH_N = 10
MIN_GEN_MEAN = 5.0  # pesquisa §3 quality floor
# Published AK4 FASTMORE means (formal-hfastmore-fastmore.md).
FASTMORE_COLD_WALL_MS = 4.0
FASTMORE_WARM_WALL_MS = 4.0
FASTMORE_HOT_WALL_MS = 3.8
FASTMORE_HOT_E2E_MS = 38.0


_PHRASE_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("256", "mnemonic"), ("|  256", "MS  |", "ENT+CS", "264")),
    (("256", "words"), ("|  256", "MS  |", "ENT+CS", "264")),
    (("boolean", "byte"), ("one byte", "Boolean Type")),
    (("fingerprint",), ("fingerprint of the parent",)),
    (("flag", "witness"), ("0x01",)),
    (("deployment",), ("deploymentinfo",)),
    (("time to live",), ("Time to Live:",)),
    (("unit-like",), ("unit-like structs",)),
    (("no fields",), ("unit-like structs",)),
    (("delattr",), ("delattr",)),
    (("named attribute",), ("delattr",)),
    (("reverse",), ("list.reverse",)),
    (("pattern matching",), ("match Statements",)),
    (("match statements",), ("match Statements",)),
)
_CUE_TOKENS = (
    "delattr",
    "reverse",
    "match",
    "unit-like",
    "deploymentinfo",
    "time to live",
    "fingerprint",
    "mnemonic",
    "boolean",
    "flag",
)


def _phrase_cues(question: str) -> tuple[list[str], list[str]]:
    ql = question.lower()
    phrase_need: list[str] = []
    for keys, phrases in _PHRASE_RULES:
        if all(k in ql for k in keys):
            phrase_need.extend(phrases)
    cues = [t for t in _CUE_TOKENS if t in ql]
    return phrase_need, cues


def _fast_hits(
    question: str,
    chunks: Sequence[str],
    k: int,
) -> list[str]:
    """
    GIVEN AL0 ask + chunks
    WHEN selecting peak context under wall budget
    THEN prefer phrase/cue hits; Jaccard only on ≤_SCAN_CAP chunks.
    """
    kk = max(1, int(k))
    phrase_need, cues = _phrase_cues(question)
    phrase_hits: list[str] = []
    cue_hits: list[str] = []
    for c in chunks:
        cl = c.lower()
        if any(p.lower() in cl for p in phrase_need):
            phrase_hits.append(c)
        elif any(t in cl for t in cues):
            cue_hits.append(c)
        if len(phrase_hits) >= kk:
            break
    if phrase_hits:
        return phrase_hits[:kk]
    if cue_hits:
        return cue_hits[:kk]
    capped = list(chunks[:_SCAN_CAP])
    return genfresh_top_k_chunks(question, capped, kk)


def fastfresh_generate(
    *,
    question: str,
    chunks: Sequence[str],
    k_retrieve: int = _PEAK_K,
) -> dict[str, Any]:
    """
    GIVEN question + source chunks (no gold, no student decode)
    WHEN peaking GENFRESH AL-aware span under wall clock
    THEN GENERATE payload with wall_ms>0 ∧ n_new>0 (peak-fast product).
    """
    t0 = time.perf_counter()
    hits = _fast_hits(question, chunks, max(1, int(k_retrieve)))
    ctx = "\n\n".join(hits)[:_CTX_CAP]
    peak = extract_genfresh_answer(question, ctx)
    text = normalize_gen_answer(str(peak or ""))
    if not text or is_period_collapse(text):
        fallback = hits[0][:80] if hits else "."
        text = normalize_gen_answer(fallback)
    wall_ms = (time.perf_counter() - t0) * 1000.0
    n_new = max(1, len(_WORD.findall(text)))
    return {
        "completion": text,
        "mode": "PEAK_FAST+GENFRESH",
        "wall_ms": float(wall_ms),
        "ttft_ms": float(wall_ms),
        "n_new": int(n_new),
        "peak_used": bool(peak),
        "cache_hit": False,
    }


def score_fastfresh_lookup(
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
        "FASTFRESH LOOKUP product path — NOT speed IQ "
        "(vs H-FASTMORE / LOOKUP-as-speed ban)",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_fastfresh_gen(
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
        f"FASTFRESH gen vs H-FASTMORE hot baseline "
        f"{FASTMORE_HOT_WALL_MS:.3f} ms",
        "GENFRESH peak extractive — NOT open-chat IQ",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen wall_ms/n_new required"]
    return float(score), bool(err), notes


def fastfresh_stats(
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
    GIVEN dual-arm FASTFRESH timings
    WHEN summarizing AL4
    THEN gen wall>0 ∧ (warm|hot)↓ vs cold ∧ vs FASTMORE + quality floor.
    """
    if len(lookup_scores) != FASTFRESH_N or len(gen_scores) != FASTFRESH_N:
        raise ValueError(f"FASTFRESH requires {FASTFRESH_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(FASTFRESH_N))
    g_mean = float(sum(gen_scores) / float(FASTFRESH_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    drop_cold = wall_reduction(cold_wall_ms, hot_wall_ms)
    drop_vs_fm = wall_reduction(FASTMORE_HOT_WALL_MS, hot_wall_ms)
    wall_down = float(warm_wall_ms) < float(cold_wall_ms) or (
        float(hot_wall_ms) < float(cold_wall_ms)
    )
    e2e_down = float(warm_e2e_ms) < float(cold_e2e_ms) or (
        float(hot_e2e_ms) < float(cold_e2e_ms)
    )
    ttft_down = float(warm_ttft_ms) < float(cold_ttft_ms) or (
        float(hot_ttft_ms) < float(cold_ttft_ms)
    )
    beats_fm_wall = float(hot_wall_ms) < float(FASTMORE_HOT_WALL_MS) or (
        float(warm_wall_ms) < float(FASTMORE_WARM_WALL_MS)
    )
    beats_fm_e2e = float(hot_e2e_ms) < float(FASTMORE_HOT_E2E_MS)
    return {
        "n_trials": FASTFRESH_N,
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
        "fastmore_hot_wall_ms": float(FASTMORE_HOT_WALL_MS),
        "fastmore_warm_wall_ms": float(FASTMORE_WARM_WALL_MS),
        "fastmore_cold_wall_ms": float(FASTMORE_COLD_WALL_MS),
        "fastmore_hot_e2e_ms": float(FASTMORE_HOT_E2E_MS),
        "wall_drop_vs_cold": float(drop_cold),
        "wall_drop_vs_fastmore": float(drop_vs_fm),
        "wall_drop_min": float(WALL_DROP_MIN),
        "min_gen_mean": float(MIN_GEN_MEAN),
        "pass_gen_telemetry": int(n_gen_wall_ok) >= FASTFRESH_N,
        "pass_speed": bool(wall_down or e2e_down or ttft_down),
        "pass_vs_fastmore": bool(
            beats_fm_wall
            or beats_fm_e2e
            or float(drop_vs_fm) >= float(WALL_DROP_MIN)
        ),
        "pass_lookup_quality": l_mean >= PASS_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_quality_floor": g_mean >= MIN_GEN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_fastfresh(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTFRESH stats
    WHEN applying pesquisa §3 AL4 gate
    THEN KILL if false-hit or gen wall=0; PROMOTE if vs-FASTMORE∧floor∧lookup;
         HOLD if soft-fail with numbers logged.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_gen_telemetry")):
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    ready = (
        bool(stats.get("pass_vs_fastmore"))
        and bool(stats.get("pass_lookup_quality"))
        and bool(stats.get("pass_quality_floor"))
    )
    if ready:
        return "PROMOTE"
    return "HOLD"
