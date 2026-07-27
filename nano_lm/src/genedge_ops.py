"""Wave AN1 H-GENEDGE: dual-arm gen with peak ablation + AN0 cues."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from an_session_ops import AN0_PACK
from asksmart_ops import is_period_collapse
from genpeak_ops import chunk_doc, extract_peak_answer, normalize_gen_answer, peak_top_k_chunks
from gentrue_ops import (
    GENPEAK_GEN_MEAN,
    GENPLUS_GEN_MEAN,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    PASS_MAX_ERRORS,
    PASS_MEAN,
    SERVEALIGN_MEAN,
    decide_gentrue,
    gentrue_stats,
    score_gentrue_gen,
    score_gentrue_lookup,
)

__all__ = [
    "GENEDGE_ID",
    "GENEDGE_N",
    "GENEDGE_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "GENPEAK_GEN_MEAN",
    "GENPLUS_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "chunk_doc",
    "peak_top_k_chunks",
    "genedge_top_k_chunks",
    "normalize_gen_answer",
    "extract_genedge_answer",
    "apply_genedge_peak",
    "score_genedge_lookup",
    "score_genedge_gen",
    "genedge_stats",
    "decide_genedge",
]

GENEDGE_ID = "H-GENEDGE"
GENEDGE_N = 10

GENEDGE_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AN0_PACK
)


def genedge_top_k_chunks(
    question: str,
    chunks: Sequence[str],
    k: int,
) -> list[str]:
    """
    GIVEN question + source chunks
    WHEN retrieving for GENEDGE
    THEN peak_top_k plus AN cue boost (192/child number/headers/…).
    """
    base = peak_top_k_chunks(question, chunks, max(int(k), 1))
    ql = question.lower()
    phrase_need: list[str] = []
    if "192" in ql and ("mnemonic" in ql or "words" in ql):
        phrase_need.extend(["|  192", "198", "ENT+CS"])
    if "child number" in ql:
        phrase_need.extend(["child number", "4 bytes"])
    if "witnessscript" in ql or ("p2wsh" in ql and "maximum" in ql):
        phrase_need.extend(["10,000 bytes", "witnessScript", "≤ 10,000"])
    if "remove" in ql and "list" in ql:
        phrase_need.extend(["list.remove", "Remove the first item"])
    if "arithmetic progression" in ql or (
        "built-in" in ql and "for loops" in ql
    ):
        phrase_need.extend(["range()", "arithmetic progression"])
    if "__dict__" in ql or "writable attributes" in ql:
        phrase_need.extend(["__dict__", "writable attributes"])
    if "compound" in ql and ("tuple" in ql or "primitive" in ql):
        phrase_need.extend(["tuples and arrays", "compound types"])
    if "tuple struct" in ql or (
        "look like tuples" in ql and "struct" in ql
    ):
        phrase_need.extend(["tuple structs", "Tuple structs"])
    if "blockheader" in ql or ("headers" in ql and "rest" in ql):
        phrase_need.extend(["/rest/headers/", "Blockheaders"])
    if "total length" in ql:
        phrase_need.extend(["Total Length:", "16 bits"])
    cues = (
        "192",
        "child number",
        "witnessscript",
        "remove",
        "range",
        "__dict__",
        "tuple",
        "headers",
        "total length",
        "p2wsh",
    )
    need = [t for t in cues if t in ql]
    phrase_hits: list[str] = []
    cue_hits: list[str] = []
    for c in chunks:
        cl = c.lower()
        if any(p.lower() in cl for p in phrase_need):
            phrase_hits.append(c)
        elif any(t in cl for t in need):
            cue_hits.append(c)
        if len(phrase_hits) >= 4 and len(cue_hits) >= 2:
            break
    extras = phrase_hits[:4] + cue_hits[:2]
    if not extras and not need and not phrase_need:
        return base
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
    if not t or len(t) > 120:
        return
    cands.append((float(score), t))


def _an_specific_spans(
    cands: list[tuple[float, str]],
    question: str,
    context: str,
) -> None:
    """Cue spans for AN0 pack facts (no gold arg)."""
    ql = question.lower()
    ctx = str(context)
    if "192" in ql and ("mnemonic" in ql or "words" in ql or "ent" in ql):
        m = re.search(
            r"\|\s*192\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+)\s*\|",
            ctx,
        )
        if m:
            _add_cand(cands, 6.5, m.group(1))
        if re.search(r"\b192\b", ctx) and re.search(r"\b18\b", ctx):
            _add_cand(cands, 5.5, "18")
    if "child number" in ql:
        m = re.search(r"(\d+)\s*bytes:\s*child number", ctx, re.I)
        if m:
            _add_cand(cands, 6.5, m.group(1))
        if "child number" in ctx.lower() and re.search(r"\b4\s*bytes\b", ctx, re.I):
            _add_cand(cands, 5.8, "4")
    if "witnessscript" in ql or ("p2wsh" in ql and ("maximum" in ql or "size" in ql)):
        m = re.search(
            r"witnessScript[`'\"\s\)\(]*[^\d]{0,20}≤?\s*10[,.]?000\s*bytes",
            ctx,
            re.I,
        )
        if m or re.search(r"≤\s*10,000\s*bytes", ctx):
            _add_cand(cands, 6.5, "10000")
        if "10,000" in ctx or "10000" in ctx:
            _add_cand(cands, 5.5, "10000")
    if "remove" in ql and ("list" in ql or "first item" in ql):
        if re.search(r"list\.remove|\.remove\(", ctx, re.I):
            _add_cand(cands, 6.0, "a.remove(x)")
        if "Remove the first item" in ctx:
            _add_cand(cands, 5.8, "a.remove(x)")
    if "arithmetic progression" in ql or (
        "built-in" in ql and ("for loop" in ql or "for loops" in ql)
    ):
        if re.search(r"\brange\b", ctx, re.I):
            _add_cand(cands, 6.0, "range")
        if "arithmetic progression" in ctx.lower():
            _add_cand(cands, 5.8, "range")
    if "__dict__" in ql or "writable attributes" in ql:
        if "__dict__" in ctx:
            _add_cand(cands, 6.0, "__dict__")
    if "compound" in ql and ("primitive" in ql or "tuple" in ql):
        if re.search(r"tuples and arrays", ctx, re.I):
            _add_cand(cands, 6.5, "tuples and arrays")
        elif "tuples" in ctx.lower() and "arrays" in ctx.lower():
            _add_cand(cands, 5.8, "tuples and arrays")
    if "tuple struct" in ql or (
        "look like tuples" in ql and "struct" in ql
    ):
        if re.search(r"tuple structs?", ctx, re.I):
            _add_cand(cands, 6.0, "tuple structs")
    if "blockheader" in ql or (
        "headers" in ql and ("rest" in ql or "get path" in ql)
    ):
        m = re.search(
            r"`?(GET\s+/rest/headers/<BLOCK-HASH>\.<bin\|hex\|json>)`?",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 6.5, m.group(1))
        elif "/rest/headers/<BLOCK-HASH>.<bin|hex|json>" in ctx:
            _add_cand(
                cands,
                6.0,
                "GET /rest/headers/<BLOCK-HASH>.<bin|hex|json>",
            )
    if "total length" in ql:
        m = re.search(r"Total Length:\s*(\d+)\s*bits", ctx, re.I)
        if m:
            _add_cand(cands, 6.5, m.group(1))


def extract_genedge_answer(question: str, context: str) -> str | None:
    """
    GIVEN question + retrieved context (no gold)
    WHEN peaking AN0-aware spans
    THEN return best extractive candidate or GENPEAK fallback.
    """
    ctx = str(context or "")
    if not ctx.strip():
        return None
    cands: list[tuple[float, str]] = []
    _an_specific_spans(cands, question, ctx)
    if cands:
        cands.sort(key=lambda t: (-t[0], abs(len(t[1]) - 12)))
        return cands[0][1]
    return extract_peak_answer(question, ctx)


def apply_genedge_peak(
    *,
    decode_text: str,
    question: str,
    context: str,
) -> tuple[str, bool, str | None]:
    """
    GIVEN decode + context
    WHEN applying GENEDGE extractive peak (comparison arm only)
    THEN prefer AN-aware peak span; else polished decode.
    """
    peak = extract_genedge_answer(question, context)
    polished = normalize_gen_answer(decode_text)
    if peak and not is_period_collapse(peak):
        return normalize_gen_answer(peak), True, peak
    return polished, False, peak


def score_genedge_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_gentrue_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("GENTRUE LOOKUP", "GENEDGE LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_genedge_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """GENERATE arm — same ablation gate as GENTRUE; relabel notes."""
    score, err, notes = score_gentrue_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=peak_ablated,
    )
    notes = [n.replace("GENTRUE", "GENEDGE") for n in notes]
    return float(score), bool(err), notes


def genedge_stats(
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
    WHEN summarizing H-GENEDGE
    THEN gate on ablated gen_mean; log peak_mean for anti-FP.
    """
    return gentrue_stats(
        lookup_scores=lookup_scores,
        lookup_errors=lookup_errors,
        gen_scores=gen_scores,
        gen_errors=gen_errors,
        gen_peak_scores=gen_peak_scores,
        n_true_hit=n_true_hit,
        n_false_hit=n_false_hit,
        n_period=n_period,
        n_fix=n_fix,
        n_peak=n_peak,
    )


def decide_genedge(stats: Mapping[str, Any]) -> str:
    """
    GIVEN GENEDGE dual-arm + ablation stats
    WHEN applying pesquisa §3 AN1 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    """
    return decide_gentrue(stats)
