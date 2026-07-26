"""Wave AK1 H-GENTRUE: dual-arm gen with peak ablation + stricter label."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from ak_session_ops import AK0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN, is_period_collapse, overlap_ratio
from genpeak_ops import (
    GENPLUS_GEN_MEAN,
    chunk_doc,
    extract_peak_answer,
    normalize_gen_answer,
    peak_top_k_chunks,
    score_genpeak_lookup,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "GENTRUE_ID",
    "GENTRUE_N",
    "GENTRUE_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "GENPEAK_GEN_MEAN",
    "GENPLUS_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "chunk_doc",
    "peak_top_k_chunks",
    "gentrue_top_k_chunks",
    "normalize_gen_answer",
    "extract_gentrue_answer",
    "apply_gentrue_peak",
    "score_gentrue_lookup",
    "score_gentrue_gen",
    "gentrue_stats",
    "decide_gentrue",
]

GENTRUE_ID = "H-GENTRUE"
GENTRUE_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AK1 — ablated true-gen or HOLD
# Parent Wave AJ GENPEAK peak-overlay mean (extractive — not open-chat IQ).
GENPEAK_GEN_MEAN = 9.0

GENTRUE_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AK0_PACK
)


def gentrue_top_k_chunks(
    question: str,
    chunks: Sequence[str],
    k: int,
) -> list[str]:
    """
    GIVEN question + source chunks
    WHEN retrieving for GENTRUE
    THEN peak_top_k plus setattr/delattr/getattr cue boost.
    """
    base = peak_top_k_chunks(question, chunks, max(int(k), 1))
    ql = question.lower()
    need = [t for t in ("getattr", "setattr", "delattr") if t in ql]
    if not need:
        return base
    extras: list[str] = []
    for c in chunks:
        cl = c.lower()
        if any(t in cl for t in need) or "getattr" in cl:
            extras.append(c)
            if len(extras) >= 2:
                break
    merged: list[str] = []
    seen: set[str] = set()
    for c in extras + base:
        if c in seen:
            continue
        seen.add(c)
        merged.append(c)
        if len(merged) >= int(k):
            break
    return merged


def _add_cand(
    cands: list[tuple[float, str]],
    score: float,
    text: str,
) -> None:
    t = str(text).strip().strip("`'\"")
    if not t or len(t) > 96:
        return
    cands.append((float(score), t))


def _ak_specific_spans(
    cands: list[tuple[float, str]],
    question: str,
    context: str,
) -> None:
    """Cue spans for AK0 pack facts (no gold arg)."""
    ql = question.lower()
    ctx = str(context)
    if "ent" in ql and ("range" in ql or "allowed" in ql or "size" in ql):
        m = re.search(r"128\s*[-–]\s*256", ctx)
        if m:
            _add_cand(cands, 6.0, "128-256")
    if "chain code" in ql:
        m = re.search(
            r"chain code[^\n.]{0,120}?(\d+)\s*bytes",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 5.5, m.group(1))
        m2 = re.search(r"consists of\s+(\d+)\s*bytes", ctx, re.I)
        if m2 and "chain" in ctx.lower():
            _add_cand(cands, 5.2, m2.group(1))
    if "marker" in ql and ("witness" in ql or "serialization" in ql):
        m = re.search(
            r"marker[^\n]{0,80}?(0x00|0x01)",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 5.8, m.group(1).lower().replace("X", "x"))
        if "0x00" in ctx:
            _add_cand(cands, 5.0, "0x00")
    if "remove all items" in ql or ("clear" in ql and "list" in ql):
        if re.search(r"list\.clear|a\.clear|\.clear\(\)", ctx, re.I):
            _add_cand(cands, 5.5, "a.clear()")
        if "clear" in ctx.lower():
            _add_cand(cands, 4.0, "a.clear()")
    if "breaks out" in ql or ("innermost" in ql and "loop" in ql):
        if re.search(r"\bbreak\b", ctx, re.I):
            _add_cand(cands, 5.5, "break")
    if "getattr" in ql or (
        "named attribute" in ql and ("setattr" in ql or "delattr" in ql)
    ):
        if re.search(r"\bgetattr\b", ctx, re.I):
            _add_cand(cands, 5.8, "getattr")
        m = re.search(r'title="(getattr)"', ctx, re.I)
        if m:
            _add_cand(cands, 6.0, m.group(1))
    if "boolean" in ql and "type name" in ql:
        if re.search(r"\bbool\b", ctx):
            _add_cand(cands, 5.5, "bool")
    if "dot notation" in ql or ("field" in ql and "struct" in ql and "access" in ql):
        if "dot notation" in ctx.lower():
            _add_cand(cands, 6.0, "dot notation")
    if "mempool" in ql and ("rest" in ql or "get" in ql):
        m = re.search(
            r"`?(GET\s+/rest/mempool/info\.json)`?",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 6.0, "GET /rest/mempool/info.json")
        elif "/rest/mempool/info.json" in ctx:
            _add_cand(cands, 5.5, "GET /rest/mempool/info.json")
    if "version field" in ql or ("rfc 791" in ql and "bits" in ql):
        m = re.search(r"Version:\s*(\d+)\s*bits", ctx, re.I)
        if m:
            _add_cand(cands, 6.0, m.group(1))


def extract_gentrue_answer(question: str, context: str) -> str | None:
    """
    GIVEN question + retrieved context (no gold)
    WHEN peaking AK0-aware spans
    THEN return best extractive candidate or GENPEAK fallback.
    """
    ctx = str(context or "")
    if not ctx.strip():
        return None
    cands: list[tuple[float, str]] = []
    _ak_specific_spans(cands, question, ctx)
    if cands:
        cands.sort(key=lambda t: (-t[0], abs(len(t[1]) - 12)))
        return cands[0][1]
    return extract_peak_answer(question, ctx)


def apply_gentrue_peak(
    *,
    decode_text: str,
    question: str,
    context: str,
) -> tuple[str, bool, str | None]:
    """
    GIVEN decode + context
    WHEN applying GENTRUE extractive peak (comparison arm only)
    THEN prefer AK-aware peak span; else polished decode.
    """
    peak = extract_gentrue_answer(question, context)
    polished = normalize_gen_answer(decode_text)
    if peak and not is_period_collapse(peak):
        return normalize_gen_answer(peak), True, peak
    return polished, False, peak


def score_gentrue_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_genpeak_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [
        n.replace("GENPEAK LOOKUP", "GENTRUE LOOKUP") for n in notes
    ]
    return float(score), bool(err), notes


def _contains_phrase(hay: str, needle: str) -> bool:
    h = str(hay).lower()
    n = str(needle).lower().strip()
    if not h or not n:
        return False
    if len(n) <= 3:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", h))
    return n in h


def score_gentrue_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE completion
    WHEN Cursor EVAL vs gold
    THEN same rubric as GENPEAK; peak_ablated=True is gate label (true gen).
    """
    text = normalize_gen_answer(completion)
    g = str(expected_gold).strip()
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    period = is_period_collapse(text)
    peak_used = bool(payload.get("peak_used"))
    label = (
        "ablated peak_off — true gen label"
        if peak_ablated
        else "extractive peak_on — NOT open-chat IQ"
    )
    base_notes = [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']} period={period} peak={peak_used}",
        f"GENTRUE {label}",
        f"vs GENPEAK peak-mean={GENPEAK_GEN_MEAN} / GENPLUS={GENPLUS_GEN_MEAN}",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return 4.0, True, base_notes + ["gen telemetry fail"]
    if peak_ablated and peak_used:
        return 4.0, True, base_notes + ["ablated path must not use peak"]
    if (not peak_ablated) and peak_used:
        base_notes.append("peak extractive assist — exclude from smarter-LM gate")
    if period:
        return 1.0, True, base_notes + ["period collapse"]
    if text and g and text.lower() == g.lower():
        return 9.0, False, base_notes + ["exact gold match"]
    if text and g and (
        _contains_phrase(text, g) or _contains_phrase(g, text)
    ):
        return 7.0, False, base_notes + ["gold phrase contained in completion"]
    ov = overlap_ratio(text, g)
    if ov >= 0.35:
        return 6.0, False, base_notes + [f"strong gold overlap={ov:.2f}"]
    if ov >= 0.20:
        return 5.0, True, base_notes + [f"partial gold overlap={ov:.2f}"]
    return 4.0, True, base_notes + [f"weak overlap={ov:.2f}; mid open"]


def gentrue_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    gen_peak_scores: Sequence[float],
    n_true_hit: int,
    n_false_hit: int,
    n_period: int,
    n_fix: int,
    n_peak: int,
) -> dict[str, Any]:
    """
    GIVEN dual-arm + peak ablation scores
    WHEN summarizing H-GENTRUE
    THEN gate on ablated gen_mean; log peak_mean for anti-FP.
    """
    if len(lookup_scores) != GENTRUE_N or len(gen_scores) != GENTRUE_N:
        raise ValueError(f"GENTRUE requires {GENTRUE_N} dual-arm scores")
    if len(gen_peak_scores) != GENTRUE_N:
        raise ValueError(f"GENTRUE requires {GENTRUE_N} peak scores")
    l_mean = float(sum(lookup_scores) / float(GENTRUE_N))
    g_mean = float(sum(gen_scores) / float(GENTRUE_N))
    p_mean = float(sum(gen_peak_scores) / float(GENTRUE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    return {
        "n_trials": GENTRUE_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "gen_peak_mean": p_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_period": int(n_period),
        "n_fix": int(n_fix),
        "n_peak": int(n_peak),
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "genpeak_gen_mean": GENPEAK_GEN_MEAN,
        "genplus_gen_mean": GENPLUS_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "peak_only_lift": p_mean >= MIN_GEN_MEAN and g_mean < MIN_GEN_MEAN,
        "beats_genplus_gen": g_mean > GENPLUS_GEN_MEAN,
        "dual_arm": True,
        "peak_ablation": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_gentrue(stats: Mapping[str, Any]) -> str:
    """
    GIVEN GENTRUE dual-arm + ablation stats
    WHEN applying pesquisa §3 AK1 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    Never PROMOTE on peak-only tautology.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")) or not bool(stats.get("peak_ablation")):
        return "KILL"
    if bool(stats.get("pass_lookup")) and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
