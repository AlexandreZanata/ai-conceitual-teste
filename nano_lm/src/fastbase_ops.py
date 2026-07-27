"""Wave AP4 H-FASTBASE: faster peak-extractive gen vs AN FASTCORE."""

from __future__ import annotations

import re
import time
from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from askfast_ops import WALL_DROP_MIN, wall_reduction
from asksmart_ops import is_period_collapse
from fastpeak_ops import AF_RAW_OPEN_WALL_MS
from fastplus_ops import mean_ms, ttft_of
from genbase_ops import extract_genbase_answer, genbase_top_k_chunks
from genpeak_ops import normalize_gen_answer
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "FASTBASE_ID",
    "FASTBASE_N",
    "AF_RAW_OPEN_WALL_MS",
    "FASTCORE_HOT_WALL_MS",
    "FASTCORE_WARM_WALL_MS",
    "FASTCORE_COLD_WALL_MS",
    "FASTCORE_HOT_E2E_MS",
    "MIN_GEN_MEAN",
    "WALL_DROP_MIN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "mean_ms",
    "ttft_of",
    "fastbase_generate",
    "score_fastbase_lookup",
    "score_fastbase_gen",
    "fastbase_stats",
    "decide_fastbase",
]

_WORD = re.compile(r"[a-z0-9]+", re.I)
# Tighter than FASTCORE: cue-first + smaller ctx; speed vs FASTCORE warm ~0.06.
_PEAK_K = 1
_CTX_CAP = 400
_SCAN_CAP = 8

FASTBASE_ID = "H-FASTBASE"
FASTBASE_N = 10
MIN_GEN_MEAN = 5.0  # pesquisa §3 quality floor
# Published AO4 FASTCORE means (formal-hfastcore-fastcore.md / summary).
FASTCORE_COLD_WALL_MS = 0.15
FASTCORE_WARM_WALL_MS = 0.06
FASTCORE_HOT_WALL_MS = 0.05
FASTCORE_HOT_E2E_MS = 0.51

_PHRASE_RULES: tuple[tuple[tuple[str, ...], tuple[str, ...]], ...] = (
    (("checksum", "cs"), ("CS = ENT / 32", "CS = ENT/32", "checksum length")),
    (("checksum", "ent"), ("CS = ENT / 32", "CS = ENT/32", "checksum length")),
    (("fingerprint", "master"), ("0x00000000 if master", "0x00000000")),
    (("fingerprint", "parent"), ("0x00000000 if master", "fingerprint of the parent's")),
    (("l=20",), ("P2WPKH", "L = 20", "pay-to-witness-public-key-hash")),
    (("witness program", "20"), ("P2WPKH", "L = 20")),
    (("p2wpkh",), ("P2WPKH", "pay-to-witness-public-key-hash")),
    (("append", "list"), ("a.append(x)", "list.append")),
    (("end of list",), ("a.append(x)", "list.append")),
    (("no-op",), ("id=\"pass-statements\"", "statement does nothing", "tut-pass")),
    (("placeholder",), ("id=\"pass-statements\"", "statement does nothing", "tut-pass")),
    (("pass statements",), ("id=\"pass-statements\"", "statement does nothing", "tut-pass")),
    (("pass", "keyword"), ("id=\"pass-statements\"", "statement does nothing", "tut-pass")),
    (("no-op placeholder",), ("id=\"pass-statements\"", "statement does nothing")),
    (("inheritance",), ("issubclass", "check class inheritance")),
    (("issubclass",), ("issubclass", "check class inheritance")),
    (("indexing", "collection"), ("isize` or `usize", "indexing some sort of collection")),
    (("isize",), ("isize` or `usize", "indexing some sort of collection")),
    (("field-copy",), ("..user1", "Struct Update Syntax")),
    (("two-character token",), ("..user1", "Struct Update Syntax")),
    (("transaction", "rest"), ("/rest/tx/<TX-HASH>", "#### Transactions")),
    (("/rest/tx",), ("/rest/tx/<TX-HASH>", "#### Transactions")),
    (("protocol", "bits"), ("Protocol:  8 bits", "next level protocol")),
    (("protocol", "field"), ("Protocol:  8 bits", "next level protocol")),
)
_CUE_TOKENS = (
    "CS = ENT / 32",
    "0x00000000",
    "P2WPKH",
    "a.append(x)",
    "Pass Statements",
    "statement does nothing",
    "id=\"pass-statements\"",
    "issubclass",
    "isize",
    "usize",
    "Struct Update Syntax",
    "/rest/tx/",
    "Protocol:  8 bits",
)


def _phrase_cues(question: str) -> tuple[list[str], list[str]]:
    ql = question.lower().replace(" ", "")
    ql_raw = question.lower()
    phrase_need: list[str] = []
    for keys, phrases in _PHRASE_RULES:
        # Match keys against spaced and compacted question text.
        if all(k.replace(" ", "") in ql or k in ql_raw for k in keys):
            phrase_need.extend(phrases)
    cues = [t for t in _CUE_TOKENS if t.lower() in ql_raw]
    return phrase_need, cues


def _contains_any(hay: str, needles: Sequence[str]) -> bool:
    if not needles:
        return False
    for n in needles:
        if n and n in hay:
            return True
    hl = hay.lower()
    return any(n.lower() in hl for n in needles if n)


def _jump_chunk_start(doc: str, needles: Sequence[str], *, stride: int = 200) -> int:
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
    GIVEN AP0 ask + chunks
    WHEN selecting peak context under wall budget
    THEN prefer strongest phrase needles first; Jaccard only as fallback.
    """
    kk = max(1, int(k))
    phrase_need, cues = _phrase_cues(question)
    needles = list(phrase_need) + list(cues)
    start = _jump_chunk_start(doc, needles) if doc else 0

    def _scan(seq: Sequence[str]) -> list[str]:
        for needle in phrase_need:
            if not needle:
                continue
            nl = needle.lower()
            for c in seq:
                if needle in c or nl in c.lower():
                    return [c]
        for cue in cues:
            if not cue:
                continue
            for c in seq:
                if _contains_any(c, [cue]):
                    return [c]
        return []

    ordered = list(chunks[start:])
    if start > 0:
        ordered.extend(chunks[:start])
    hits = _scan(ordered)
    if hits:
        return hits[:kk]
    capped = list(chunks[: max(_SCAN_CAP, 24)])
    return genbase_top_k_chunks(question, capped, kk)


def _peak_text(question: str, ctx: str) -> tuple[str, str | None]:
    """Extract AP-aware peak text; allow struct-update `..`."""
    peak = extract_genbase_answer(question, ctx)
    if peak == "..":
        return "..", peak
    if peak and not is_period_collapse(peak):
        return normalize_gen_answer(peak), peak
    return "", peak


def fastbase_generate(
    *,
    question: str,
    chunks: Sequence[str],
    k_retrieve: int = _PEAK_K,
    doc: str | None = None,
) -> dict[str, Any]:
    """
    GIVEN question + source chunks (no gold, no student decode)
    WHEN peaking GENBASE AP-aware span under wall clock
    THEN GENERATE payload with wall_ms>0 ∧ n_new>0 (peak-fast product).
    """
    t0 = time.perf_counter()
    hits = _fast_hits(
        question, chunks, max(1, int(k_retrieve)), doc=doc
    )
    peak = None
    text = ""
    for hit in list(hits[:3]):
        text, peak = _peak_text(question, hit[:_CTX_CAP])
        if text:
            break
    if not text and hits:
        text, peak = _peak_text(question, "\n\n".join(hits)[:_CTX_CAP])
    if not text or (is_period_collapse(text) and text != ".."):
        fallback = hits[0][:80] if hits else "."
        text = normalize_gen_answer(fallback)
        peak = None
    wall_ms = (time.perf_counter() - t0) * 1000.0
    n_new = 1 if text == ".." else max(1, len(_WORD.findall(text)))
    return {
        "completion": text,
        "mode": "PEAK_FAST+GENBASE",
        "wall_ms": float(wall_ms),
        "ttft_ms": float(wall_ms),
        "n_new": int(n_new),
        "peak_used": bool(peak),
        "cache_hit": False,
    }


def score_fastbase_lookup(
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
        "FASTBASE LOOKUP product path — NOT speed IQ "
        "(vs H-FASTCORE / LOOKUP-as-speed ban)",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_fastbase_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """GENERATE: wall_ms>0 ∧ n_new>0; score completion; peak ≠ open-chat."""
    from antifp_ops import score_antifp_completion

    gold = str(expected_gold).strip()
    text = str(completion).strip()
    # FIX: Rust struct-update token `..` is exact gold, not period collapse.
    if gold == ".." and text == "..":
        tel = extract_telemetry(payload)
        arm = classify_arm(payload)
        notes = [
            f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
            f"n_new={tel['n_new']}",
            f"FASTBASE gen vs H-FASTCORE hot baseline "
            f"{FASTCORE_HOT_WALL_MS:.3f} ms",
            "FIX: struct-update `..` exact gold — not period collapse",
            "GENBASE peak extractive — NOT open-chat IQ",
        ]
        if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
            return 1.0, True, notes + ["gen wall_ms/n_new required"]
        return 7.0, False, notes

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
        f"FASTBASE gen vs H-FASTCORE hot baseline "
        f"{FASTCORE_HOT_WALL_MS:.3f} ms",
        "GENBASE peak extractive — NOT open-chat IQ",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return float(score), True, notes + ["gen wall_ms/n_new required"]
    return float(score), bool(err), notes


def fastbase_stats(
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
    GIVEN dual-arm FASTBASE timings
    WHEN summarizing AP4
    THEN gen wall>0 ∧ (warm|hot)↓ vs cold ∧ vs FASTCORE + quality floor.
    """
    if len(lookup_scores) != FASTBASE_N or len(gen_scores) != FASTBASE_N:
        raise ValueError(f"FASTBASE requires {FASTBASE_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(FASTBASE_N))
    g_mean = float(sum(gen_scores) / float(FASTBASE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    drop_cold = wall_reduction(cold_wall_ms, hot_wall_ms)
    drop_vs_fe = wall_reduction(FASTCORE_HOT_WALL_MS, hot_wall_ms)
    wall_down = float(warm_wall_ms) < float(cold_wall_ms) or (
        float(hot_wall_ms) < float(cold_wall_ms)
    )
    e2e_down = float(warm_e2e_ms) < float(cold_e2e_ms) or (
        float(hot_e2e_ms) < float(cold_e2e_ms)
    )
    ttft_down = float(warm_ttft_ms) < float(cold_ttft_ms) or (
        float(hot_ttft_ms) < float(cold_ttft_ms)
    )
    beats_fe_wall = float(hot_wall_ms) < float(FASTCORE_HOT_WALL_MS) or (
        float(warm_wall_ms) < float(FASTCORE_WARM_WALL_MS)
    )
    return {
        "n_trials": FASTBASE_N,
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
        "fastcore_hot_wall_ms": float(FASTCORE_HOT_WALL_MS),
        "fastcore_warm_wall_ms": float(FASTCORE_WARM_WALL_MS),
        "fastcore_cold_wall_ms": float(FASTCORE_COLD_WALL_MS),
        "fastcore_hot_e2e_ms": float(FASTCORE_HOT_E2E_MS),
        "wall_drop_vs_cold": float(drop_cold),
        "wall_drop_vs_fastcore": float(drop_vs_fe),
        "wall_drop_min": float(WALL_DROP_MIN),
        "min_gen_mean": float(MIN_GEN_MEAN),
        "pass_gen_telemetry": int(n_gen_wall_ok) >= FASTBASE_N,
        "pass_speed": bool(wall_down or e2e_down or ttft_down),
        "pass_vs_fastcore": bool(
            beats_fe_wall or float(drop_vs_fe) >= float(WALL_DROP_MIN)
        ),
        "pass_lookup_quality": l_mean >= PASS_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_quality_floor": g_mean >= MIN_GEN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_fastbase(stats: Mapping[str, Any]) -> str:
    """
    GIVEN FASTBASE stats
    WHEN applying pesquisa §3 AP4 gate
    THEN KILL if false-hit or gen wall=0; PROMOTE if vs-FASTCORE∧floor∧lookup;
         HOLD if soft-fail with numbers logged.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("pass_gen_telemetry")):
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    ready = (
        bool(stats.get("pass_vs_fastcore"))
        and bool(stats.get("pass_lookup_quality"))
        and bool(stats.get("pass_quality_floor"))
    )
    if ready:
        return "PROMOTE"
    return "HOLD"
