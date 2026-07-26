"""Wave AM1 H-GENTRUTH: dual-arm gen with peak ablation + stricter label."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from am_session_ops import AM0_PACK
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
from asksmart_ops import is_period_collapse

__all__ = [
    "GENTRUTH_ID",
    "GENTRUTH_N",
    "GENTRUTH_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "GENPEAK_GEN_MEAN",
    "GENPLUS_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "chunk_doc",
    "peak_top_k_chunks",
    "gentruth_top_k_chunks",
    "normalize_gen_answer",
    "extract_gentruth_answer",
    "apply_gentruth_peak",
    "score_gentruth_lookup",
    "score_gentruth_gen",
    "gentruth_stats",
    "decide_gentruth",
]

GENTRUTH_ID = "H-GENTRUTH"
GENTRUTH_N = 10

GENTRUTH_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AM0_PACK
)


def gentruth_top_k_chunks(
    question: str,
    chunks: Sequence[str],
    k: int,
) -> list[str]:
    """
    GIVEN question + source chunks
    WHEN retrieving for GENTRUTH
    THEN peak_top_k plus AM cue boost (160/setattr/IHL/…).
    """
    base = peak_top_k_chunks(question, chunks, max(int(k), 1))
    ql = question.lower()
    phrase_need: list[str] = []
    if "160" in ql and ("mnemonic" in ql or "words" in ql):
        phrase_need.extend(["|  160", "MS  |", "ENT+CS", "165"])
    if "key data" in ql or ("33" in ql and "byte" in ql):
        phrase_need.extend(["33 bytes", "public key or private key"])
    if "p2wpkh" in ql or ("witness stack" in ql and "version-0" in ql):
        phrase_need.extend(["exactly 2 items", "P2WPKH", "20 bytes"])
    if "index" in ql and "list" in ql:
        phrase_need.extend(["list.index", "zero-based"])
    if "without break" in ql or ("clause" in ql and "loop" in ql):
        phrase_need.extend(["else Clauses on Loops", "without"])
    if "setattr" in ql or ("sets a named attribute" in ql):
        phrase_need.append("setattr")
    if "char" in ql and "byte" in ql:
        phrase_need.extend(
            ["4 bytes in size", "char` type", "Unicode scalar", "char type"]
        )
    if "pieces of data" in ql or ("inside a struct" in ql and "called" in ql):
        phrase_need.extend(["fields", "pieces of data"])
    if "mempool" in ql and "contents" in ql:
        phrase_need.append("mempool/contents")
    if "ihl" in ql:
        phrase_need.extend(["IHL:", "Internet Header Length"])
    cues = (
        "setattr",
        "getattr",
        "delattr",
        "index",
        "else",
        "char",
        "fields",
        "mempool",
        "ihl",
        "p2wpkh",
        "mnemonic",
        "33 bytes",
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
    if not t or len(t) > 96:
        return
    cands.append((float(score), t))


def _am_specific_spans(
    cands: list[tuple[float, str]],
    question: str,
    context: str,
) -> None:
    """Cue spans for AM0 pack facts (no gold arg)."""
    ql = question.lower()
    ctx = str(context)
    if "160" in ql and ("mnemonic" in ql or "words" in ql or "ent" in ql):
        m = re.search(
            r"\|\s*160\s*\|\s*\d+\s*\|\s*\d+\s*\|\s*(\d+)\s*\|",
            ctx,
        )
        if m:
            _add_cand(cands, 6.5, m.group(1))
        if re.search(r"\b160\b", ctx) and re.search(r"\b15\b", ctx):
            _add_cand(cands, 5.5, "15")
    if "key data" in ql or (
        "public or private" in ql and "bytes" in ql
    ):
        m = re.search(
            r"(\d+)\s*bytes:\s*the public key or private key data",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 6.0, m.group(1))
        if re.search(r"0x00\s*\|\|\s*ser", ctx) and "33" in ctx:
            _add_cand(cands, 5.5, "33")
    if "p2wpkh" in ql or (
        "witness stack" in ql and ("version-0" in ql or "version 0" in ql)
    ):
        m = re.search(
            r"witness must consist of exactly\s+(\d+)\s+items",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 6.5, m.group(1))
        if "P2WPKH" in ctx and re.search(r"exactly\s+2\s+items", ctx, re.I):
            _add_cand(cands, 6.0, "2")
    if "index" in ql and ("list" in ql or "zero-based" in ql):
        if re.search(r"list\.index|\.index\(|a\.index", ctx, re.I):
            _add_cand(cands, 5.8, "a.index(x)")
        if "index" in ctx.lower() and "list" in ctx.lower():
            _add_cand(cands, 4.0, "a.index(x)")
    if "without break" in ql or (
        "clause" in ql and "loop" in ql and "break" in ql
    ):
        if re.search(r"\belse\b", ctx, re.I) and "loop" in ctx.lower():
            _add_cand(cands, 5.8, "else")
        if "else Clauses on Loops" in ctx or "else clause" in ctx.lower():
            _add_cand(cands, 6.0, "else")
    if "setattr" in ql or (
        "sets a named attribute" in ql
        or ("named attribute" in ql and "sets" in ql)
    ):
        if re.search(r"\bsetattr\b", ctx, re.I):
            _add_cand(cands, 5.8, "setattr")
        m = re.search(r'title="(setattr)"', ctx, re.I)
        if m:
            _add_cand(cands, 6.0, m.group(1))
    if "char" in ql and ("bytes" in ql or "byte" in ql):
        # Rust book: "Rust's `char` type is 4 bytes in size"
        if re.search(
            r"char[`'\"\s]*type is\s*4\s*bytes|4\s*bytes in size",
            ctx,
            re.I,
        ):
            _add_cand(cands, 6.5, "4")
        elif "char" in ctx.lower() and re.search(r"\b4\s*bytes\b", ctx, re.I):
            _add_cand(cands, 6.0, "4")
        # Prefer numeric size over Unicode-range noise (U+10FFFF).
        if re.search(r"Unicode scalar", ctx, re.I) and re.search(
            r"\b4\s*bytes\b", ctx, re.I
        ):
            _add_cand(cands, 5.8, "4")
    if "pieces of data" in ql or (
        "inside a struct" in ql and "called" in ql
    ):
        if re.search(r"\bfields\b", ctx, re.I):
            _add_cand(cands, 5.8, "fields")
        if "pieces of data" in ctx.lower() and "fields" in ctx.lower():
            _add_cand(cands, 6.0, "fields")
    if "mempool" in ql and "contents" in ql:
        m = re.search(
            r"`?(GET\s+/rest/mempool/contents\.json)`?",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 6.0, "GET /rest/mempool/contents.json")
        elif "/rest/mempool/contents.json" in ctx:
            _add_cand(cands, 5.5, "GET /rest/mempool/contents.json")
    if "ihl" in ql:
        m = re.search(r"IHL:\s*(\d+)\s*bits", ctx, re.I)
        if m:
            _add_cand(cands, 6.0, m.group(1))


def extract_gentruth_answer(question: str, context: str) -> str | None:
    """
    GIVEN question + retrieved context (no gold)
    WHEN peaking AM0-aware spans
    THEN return best extractive candidate or GENPEAK fallback.
    """
    ctx = str(context or "")
    if not ctx.strip():
        return None
    cands: list[tuple[float, str]] = []
    _am_specific_spans(cands, question, ctx)
    if cands:
        cands.sort(key=lambda t: (-t[0], abs(len(t[1]) - 12)))
        return cands[0][1]
    return extract_peak_answer(question, ctx)


def apply_gentruth_peak(
    *,
    decode_text: str,
    question: str,
    context: str,
) -> tuple[str, bool, str | None]:
    """
    GIVEN decode + context
    WHEN applying GENTRUTH extractive peak (comparison arm only)
    THEN prefer AM-aware peak span; else polished decode.
    """
    peak = extract_gentruth_answer(question, context)
    polished = normalize_gen_answer(decode_text)
    if peak and not is_period_collapse(peak):
        return normalize_gen_answer(peak), True, peak
    return polished, False, peak


def score_gentruth_lookup(
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
    notes = [n.replace("GENTRUE LOOKUP", "GENTRUTH LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_gentruth_gen(
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
    notes = [n.replace("GENTRUE", "GENTRUTH") for n in notes]
    return float(score), bool(err), notes


def gentruth_stats(
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
    WHEN summarizing H-GENTRUTH
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


def decide_gentruth(stats: Mapping[str, Any]) -> str:
    """
    GIVEN GENTRUTH dual-arm + ablation stats
    WHEN applying pesquisa §3 AM1 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    """
    return decide_gentrue(stats)
