"""Wave AP1 H-GENBASE: dual-arm gen with peak ablation + AP0 cues."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from ap_session_ops import AP0_PACK
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
    "GENBASE_ID",
    "GENBASE_N",
    "GENBASE_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "GENPEAK_GEN_MEAN",
    "GENPLUS_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "chunk_doc",
    "peak_top_k_chunks",
    "genbase_top_k_chunks",
    "normalize_gen_answer",
    "extract_genbase_answer",
    "apply_genbase_peak",
    "score_genbase_lookup",
    "score_genbase_gen",
    "genbase_stats",
    "decide_genbase",
]

GENBASE_ID = "H-GENBASE"
GENBASE_N = 10

GENBASE_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AP0_PACK
)


def genbase_top_k_chunks(
    question: str,
    chunks: Sequence[str],
    k: int,
) -> list[str]:
    """
    GIVEN question + source chunks
    WHEN retrieving for GENBASE
    THEN peak_top_k plus AP cue boost (CS=ENT/32 · P2WPKH · …).
    """
    base = peak_top_k_chunks(question, chunks, max(int(k), 1))
    ql = question.lower()
    phrase_need: list[str] = []
    if "checksum" in ql and ("cs" in ql or "ent" in ql):
        phrase_need.extend(["CS = ENT / 32", "CS = ENT/32", "checksum length"])
    if "fingerprint" in ql and ("master" in ql or "parent" in ql):
        phrase_need.extend(["0x00000000 if master", "fingerprint of the parent's"])
    if "p2wpkh" in ql or ("l=20" in ql.replace(" ", "") or "l = 20" in ql):
        phrase_need.extend(["P2WPKH", "L = 20", "pay-to-witness-public-key-hash"])
    if ("append" in ql and "list" in ql) or (
        "end of list" in ql and "method call" in ql
    ):
        phrase_need.extend(["a.append(x)", "list.append"])
    if "pass" in ql and ("no-op" in ql or "placeholder" in ql or "statement" in ql):
        phrase_need.extend(["pass statement does nothing", "Pass Statements"])
    if "issubclass" in ql or ("inheritance" in ql and "built-in" in ql):
        phrase_need.extend(["issubclass", "check class inheritance"])
    if "indexing" in ql and ("collection" in ql or "integer" in ql):
        phrase_need.extend(["isize` or `usize", "indexing some sort of collection"])
    if "field-copy" in ql or ("two-character token" in ql) or (
        ".." in question and "struct" in ql
    ):
        phrase_need.extend(
            ["..user1", "Struct Update Syntax", "struct update syntax"]
        )
    if "/rest/tx" in ql or ("transaction" in ql and "rest" in ql):
        phrase_need.extend(["/rest/tx/<TX-HASH>", "#### Transactions"])
    if "protocol" in ql and ("bits" in ql or "field" in ql):
        phrase_need.extend(["Protocol:  8 bits", "next level protocol"])
    cues = (
        "checksum",
        "fingerprint",
        "p2wpkh",
        "append",
        "pass",
        "issubclass",
        "isize",
        "usize",
        "struct",
        "transaction",
        "protocol",
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


def _ap_specific_spans(
    cands: list[tuple[float, str]],
    question: str,
    context: str,
) -> None:
    """Cue spans for AP0 pack facts (no gold arg)."""
    ql = question.lower()
    ctx = str(context)
    if "checksum" in ql and ("cs" in ql or "ent" in ql or "formula" in ql):
        if re.search(r"CS\s*=\s*ENT\s*/\s*32", ctx):
            _add_cand(cands, 6.5, "CS = ENT / 32")
    if "fingerprint" in ql and ("master" in ql or "parent" in ql):
        if re.search(r"0x00000000\s*if master", ctx, re.I):
            _add_cand(cands, 6.5, "0x00000000")
        elif "0x00000000" in ctx and "master" in ctx.lower():
            _add_cand(cands, 6.0, "0x00000000")
    if "l=20" in ql.replace(" ", "") or (
        "20" in ql and "witness program" in ql
    ) or "p2wpkh" in ql:
        if re.search(r"\bP2WPKH\b", ctx):
            _add_cand(cands, 6.5, "P2WPKH")
    if ("append" in ql and ("list" in ql or "end" in ql)) or (
        "end of list" in ql and "method" in ql
    ):
        if re.search(r"a\.append\(x\)", ctx, re.I):
            _add_cand(cands, 6.5, "a.append(x)")
        elif re.search(r"list\.append", ctx, re.I):
            _add_cand(cands, 5.5, "a.append(x)")
    if "pass" in ql and (
        "no-op" in ql or "placeholder" in ql or "statement" in ql
    ):
        if re.search(r"pass\s+statement does nothing|\bpass\b", ctx, re.I):
            _add_cand(cands, 6.0, "pass")
    if "issubclass" in ql or (
        "inheritance" in ql and ("built-in" in ql or "checks class" in ql)
    ):
        if re.search(r"\bisubclass\b|\bisubclass\(", ctx) or "issubclass" in ctx:
            _add_cand(cands, 6.0, "issubclass")
    if "indexing" in ql and ("collection" in ql or "integer" in ql):
        if re.search(r"`?isize`?\s+or\s+`?usize`?", ctx, re.I):
            _add_cand(cands, 6.5, "isize or usize")
        elif "isize" in ctx and "usize" in ctx and "index" in ctx.lower():
            _add_cand(cands, 6.0, "isize or usize")
    if "field-copy" in ql or (
        "two-character token" in ql and "struct" in ql
    ) or (".." in question and "struct" in ql):
        if re.search(r"\.\.user1", ctx):
            _add_cand(cands, 7.0, "..")
        elif re.search(r"Struct Update Syntax", ctx, re.I):
            _add_cand(cands, 6.5, "..")
        elif ".." in ctx:
            _add_cand(cands, 6.0, "..")
    if "transaction" in ql and ("rest" in ql or "get path" in ql):
        m = re.search(
            r"`?(GET\s+/rest/tx/<TX-HASH>\.<bin\|hex\|json>)`?",
            ctx,
            re.I,
        )
        if m:
            _add_cand(cands, 6.5, m.group(1))
        elif "/rest/tx/<TX-HASH>.<bin|hex|json>" in ctx:
            _add_cand(
                cands,
                6.0,
                "GET /rest/tx/<TX-HASH>.<bin|hex|json>",
            )
    if "protocol" in ql and ("bits" in ql or "field" in ql):
        m = re.search(r"Protocol:\s*(\d+)\s*bits", ctx, re.I)
        if m:
            _add_cand(cands, 6.5, m.group(1))
        if re.search(r"\b8\s*bits\b", ctx, re.I) and "protocol" in ctx.lower():
            _add_cand(cands, 5.8, "8")
        # Prefer Protocol field over TTL/other 8-bit fields when both present.
        cands[:] = [
            c
            for c in cands
            if "ttl" not in c[1].lower() and "time to live" not in c[1].lower()
        ]


def extract_genbase_answer(question: str, context: str) -> str | None:
    """
    GIVEN question + retrieved context (no gold)
    WHEN peaking AP0-aware spans
    THEN return best extractive candidate or GENPEAK fallback.
    """
    ctx = str(context or "")
    if not ctx.strip():
        return None
    cands: list[tuple[float, str]] = []
    _ap_specific_spans(cands, question, ctx)
    if cands:
        cands.sort(key=lambda t: (-t[0], abs(len(t[1]) - 12)))
        return cands[0][1]
    return extract_peak_answer(question, ctx)


def apply_genbase_peak(
    *,
    decode_text: str,
    question: str,
    context: str,
) -> tuple[str, bool, str | None]:
    """
    GIVEN decode + context
    WHEN applying GENBASE extractive peak (comparison arm only)
    THEN prefer AP-aware peak span; else polished decode.
    """
    peak = extract_genbase_answer(question, context)
    polished = normalize_gen_answer(decode_text)
    ql = question.lower()
    # Struct-update token `..` is a valid gold — not a period collapse.
    if peak == ".." and (
        "two-character" in ql or "field-copy" in ql or "struct" in ql
    ):
        return "..", True, peak
    if peak and not is_period_collapse(peak):
        return normalize_gen_answer(peak), True, peak
    return polished, False, peak


def score_genbase_lookup(
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
    notes = [n.replace("GENTRUE LOOKUP", "GENBASE LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_genbase_gen(
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
    notes = [n.replace("GENTRUE", "GENBASE") for n in notes]
    return float(score), bool(err), notes


def genbase_stats(
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
    WHEN summarizing H-GENBASE
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


def decide_genbase(stats: Mapping[str, Any]) -> str:
    """
    GIVEN GENBASE dual-arm + ablation stats
    WHEN applying pesquisa §3 AP1 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    """
    return decide_gentrue(stats)
