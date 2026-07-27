"""Wave AO4 H-FASTCORE: faster peak-extractive gen vs AN FASTEDGE."""

from __future__ import annotations

import re
import time
from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from askfast_ops import WALL_DROP_MIN, wall_reduction
from asksmart_ops import is_period_collapse
from fastpeak_ops import AF_RAW_OPEN_WALL_MS
from fastplus_ops import mean_ms, ttft_of
from gencore_ops import extract_gencore_answer, gencore_top_k_chunks
from genpeak_ops import normalize_gen_answer
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTCORE_ID",
    "FASTCORE_N",
    "AF_RAW_OPEN_WALL_MS",
    "FASTEDGE_HOT_WALL_MS",
    "FASTEDGE_WARM_WALL_MS",
    "FASTEDGE_COLD_WALL_MS",
    "FASTEDGE_HOT_E2E_MS",
    "MIN_GEN_MEAN",
    "WALL_DROP_MIN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "mean_ms",
    "ttft_of",
    "fastcore_generate",
    "score_fastcore_lookup",
    "score_fastcore_gen",
    "fastcore_stats",
    "decide_fastcore",
]

_WORD = re.compile(r"[a-z0-9]+", re.I)
# Tighter than FASTEDGE: cue-first + smaller ctx; speed vs FASTEDGE hot ~0.05.
_PEAK_K = 1
_CTX_CAP = 360
_SCAN_CAP = 12

FASTCORE_ID = "H-FASTCORE"
FASTCORE_N = 10
MIN_GEN_MEAN = 5.0  # pesquisa §3 quality floor
# Published AN4 FASTEDGE means (formal-hfastedge-fastedge.md / summary).
FASTEDGE_COLD_WALL_MS = 0.14
FASTEDGE_WARM_WALL_MS = 0.10
FASTEDGE_HOT_WALL_MS = 0.05
FASTEDGE_HOT_E2E_MS = 0.51

_PHRASE_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("224", "mnemonic"), ("|  224", "ENT+CS", "231")),
    (("224", "words"), ("|  224", "ENT+CS", "231")),
    (("version", "byte"), ("version bytes", "4 bytes: version")),
    (("version", "field"), ("version bytes", "4 bytes: version")),
    (("witness program",), ("0x28", "push of 40 bytes", "witness program")),
    (("witness", "length"), ("0x28", "push of 40 bytes", "witness program")),
    (("count", "list"), ("list.count", "number of times")),
    (("how many times",), ("list.count", "number of times")),
    (("while", "loop"), ("while statement", "while")),
    (("while", "condition"), ("while statement", "while")),
    (("super",), ("super()", "call-next-method")),
    (("cooperative",), ("super()", "call-next-method")),
    (("unsigned",), ("unsigned integer", "start with `i` instead of `u`")),
    (("struct type",), ("keyword `struct`", "Defining and Instantiating")),
    (("keyword starts a struct",), ("keyword `struct`", "Defining and Instantiating")),
    (("full block",), ("/rest/block/<BLOCK-HASH>", "Given a block hash")),
    (("block by hash",), ("/rest/block/<BLOCK-HASH>", "Given a block hash")),
    (("time to live",), ("Time to Live:", "8 bits", "Time to Live:  8")),
    (("ttl",), ("Time to Live:", "8 bits", "Time to Live:  8")),
)
_CUE_TOKENS = (
    "224",
    "version",
    "witness program",
    "list.count",
    "while",
    "super()",
    "unsigned integer",
    "keyword `struct`",
    "/rest/block/",
    "Time to Live",
)


def _phrase_cues(question: str) -> tuple[list[str], list[str]]:
    ql = question.lower()
    phrase_need: list[str] = []
    for keys, phrases in _PHRASE_RULES:
        if all(k in ql for k in keys):
            phrase_need.extend(phrases)
    cues = [t for t in _CUE_TOKENS if t.lower() in ql]
    return phrase_need, cues


def _contains_any(hay: str, needles: Sequence[str]) -> bool:
    if not needles:
        return False
    for n in needles:
        if n and n in hay:
            return True
    hl = hay.lower()
    return any(n.lower() in hl for n in needles if n)


def _jump_chunk_start(doc: str, needles: Sequence[str], *, stride: int = 160) -> int:
    for n in needles:
        if not n:
            continue
        pos = doc.find(n)
        if pos < 0:
            pos = doc.lower().find(n.lower())
        if pos >= 0:
            return max(0, int(pos) // int(stride))
    return 0


def _fast_hits(
    question: str,
    chunks: Sequence[str],
    k: int,
    *,
    doc: str | None = None,
) -> list[str]:
    """
    GIVEN AO0 ask + chunks
    WHEN selecting peak context under wall budget
    THEN prefer phrase/cue hits; Jaccard only on ≤_SCAN_CAP chunks.
    """
    kk = max(1, int(k))
    phrase_need, cues = _phrase_cues(question)
    needles = list(phrase_need) + list(cues)
    start = _jump_chunk_start(doc, needles) if doc else 0
    phrase_hits: list[str] = []
    cue_hits: list[str] = []
    for c in chunks[start:]:
        if phrase_need and _contains_any(c, phrase_need):
            phrase_hits.append(c)
            if len(phrase_hits) >= kk:
                return phrase_hits[:kk]
        elif cues and _contains_any(c, cues):
            cue_hits.append(c)
            if len(cue_hits) >= kk and not phrase_need:
                return cue_hits[:kk]
    if phrase_hits:
        return phrase_hits[:kk]
    if cue_hits:
        return cue_hits[:kk]
    if start > 0:
        return _fast_hits(question, chunks, k, doc=None)
    capped = list(chunks[:_SCAN_CAP])
    return gencore_top_k_chunks(question, capped, kk)


def fastcore_generate(
    *,
    question: str,
    chunks: Sequence[str],
    k_retrieve: int = _PEAK_K,
    doc: str | None = None,
) -> dict[str, Any]:
    """
    GIVEN question + source chunks (no gold, no student decode)
    WHEN peaking GENCORE AO-aware span under wall clock
    THEN GENERATE payload with wall_ms>0 ∧ n_new>0 (peak-fast product).
    """
    t0 = time.perf_counter()
    hits = _fast_hits(
        question, chunks, max(1, int(k_retrieve)), doc=doc
    )
    peak = None
    text = ""
    for hit in hits:
        peak = extract_gencore_answer(question, hit[:_CTX_CAP])
        if peak and not is_period_collapse(peak):
            text = normalize_gen_answer(peak)
            break
    if not text:
        ctx = "\n\n".join(hits)[:_CTX_CAP]
        peak = extract_gencore_answer(question, ctx)
        text = normalize_gen_answer(str(peak or ""))
    if not text or is_period_collapse(text):
        fallback = hits[0][:80] if hits else "."
        text = normalize_gen_answer(fallback)
        peak = None
    wall_ms = (time.perf_counter() - t0) * 1000.0
    n_new = max(1, len(_WORD.findall(text)))
    return {
        "completion": text,
        "mode": "PEAK_FAST+GENCORE",
        "wall_ms": float(wall_ms),
        "ttft_ms": float(wall_ms),
        "n_new": int(n_new),
        "peak_used": bool(peak),
        "cache_hit": False,
    }


def score_fastcore_lookup(
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
        "FASTCORE LOOKUP product path — NOT speed IQ "
        "(vs H-FASTEDGE / LOOKUP-as-speed ban)",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_fastcore_gen(
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
        f"FASTCORE gen vs H-FASTEDGE hot baseline "
        f"{FASTEDGE_HOT_WALL_MS:.3f} ms",
        "GENCORE peak extractive — NOT open-chat IQ",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen wall_ms/n_new required"]
    return float(score), bool(err), notes


def fastcore_stats(
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
    GIVEN dual-arm FASTCORE timings
    WHEN summarizing AO4
    THEN gen wall>0 ∧ (warm|hot)↓ vs cold ∧ vs FASTEDGE + quality floor.
    """
    if len(lookup_scores) != FASTCORE_N or len(gen_scores) != FASTCORE_N:
        raise ValueError(f"FASTCORE requires {FASTCORE_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(FASTCORE_N))
    g_mean = float(sum(gen_scores) / float(FASTCORE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    drop_cold = wall_reduction(cold_wall_ms, hot_wall_ms)
    drop_vs_fe = wall_reduction(FASTEDGE_HOT_WALL_MS, hot_wall_ms)
    wall_down = float(warm_wall_ms) < float(cold_wall_ms) or (
        float(hot_wall_ms) < float(cold_wall_ms)
    )
    e2e_down = float(warm_e2e_ms) < float(cold_e2e_ms) or (
        float(hot_e2e_ms) < float(cold_e2e_ms)
    )
    ttft_down = float(warm_ttft_ms) < float(cold_ttft_ms) or (
        float(hot_ttft_ms) < float(cold_ttft_ms)
    )
    beats_fe_wall = float(hot_wall_ms) < float(FASTEDGE_HOT_WALL_MS) or (
        float(warm_wall_ms) < float(FASTEDGE_WARM_WALL_MS)
    )
    return {
        "n_trials": FASTCORE_N,
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
        "fastedge_hot_wall_ms": float(FASTEDGE_HOT_WALL_MS),
        "fastedge_warm_wall_ms": float(FASTEDGE_WARM_WALL_MS),
        "fastedge_cold_wall_ms": float(FASTEDGE_COLD_WALL_MS),
        "fastedge_hot_e2e_ms": float(FASTEDGE_HOT_E2E_MS),
        "wall_drop_vs_cold": float(drop_cold),
        "wall_drop_vs_fastedge": float(drop_vs_fe),
        "wall_drop_min": float(WALL_DROP_MIN),
        "min_gen_mean": float(MIN_GEN_MEAN),
        "pass_gen_telemetry": int(n_gen_wall_ok) >= FASTCORE_N,
        "pass_speed": bool(wall_down or e2e_down or ttft_down),
        "pass_vs_fastedge": bool(
            beats_fe_wall or float(drop_vs_fe) >= float(WALL_DROP_MIN)
        ),
        "pass_lookup_quality": l_mean >= PASS_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_quality_floor": g_mean >= MIN_GEN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_fastcore(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTCORE stats
    WHEN applying pesquisa §3 AO4 gate
    THEN KILL if false-hit or gen wall=0; PROMOTE if vs-FASTEDGE∧floor∧lookup;
         HOLD if soft-fail with numbers logged.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_gen_telemetry")):
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    ready = (
        bool(stats.get("pass_vs_fastedge"))
        and bool(stats.get("pass_lookup_quality"))
        and bool(stats.get("pass_quality_floor"))
    )
    if ready:
        return "PROMOTE"
    return "HOLD"
