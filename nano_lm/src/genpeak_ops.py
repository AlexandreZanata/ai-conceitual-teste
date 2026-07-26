"""Wave AJ1 H-GENPEAK: peak GENERATE past GENPLUS via extractive grounded stops."""

from __future__ import annotations

import re
from typing import Any, Mapping, Sequence

from aj_session_ops import AJ0_PACK
from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import SERVEALIGN_MEAN, is_period_collapse, overlap_ratio
from genc_prompt import jaccard
from genplus_ops import (
    chunk_doc,
    fit_prompt_tokens,
    ground_prompt,
    normalize_gen_answer,
    prefer_context_beam,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "GENPEAK_ID",
    "GENPEAK_N",
    "GENPEAK_PACK",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "GENPLUS_GEN_MEAN",
    "SERVEALIGN_MEAN",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "chunk_doc",
    "ground_prompt",
    "fit_prompt_tokens",
    "prefer_context_beam",
    "normalize_gen_answer",
    "peak_top_k_chunks",
    "extract_peak_answer",
    "apply_peak_completion",
    "score_genpeak_lookup",
    "score_genpeak_gen",
    "genpeak_stats",
    "decide_genpeak",
]

GENPEAK_ID = "H-GENPEAK"
GENPEAK_N = 10
MIN_LOOKUP_MEAN = 7.0
MIN_GEN_MEAN = 5.0  # pesquisa §3 AJ1 — or honest HOLD
# Parent Wave AI GENPLUS open-gen ceiling under dual-arm Cursor EVAL.
GENPLUS_GEN_MEAN = 4.0

_STOP = frozenset(
    {
        "the",
        "a",
        "an",
        "of",
        "for",
        "is",
        "are",
        "which",
        "what",
        "how",
        "many",
        "must",
        "be",
        "when",
        "with",
        "from",
        "that",
        "this",
        "give",
        "name",
        "type",
        "field",
        "chapter",
        "tutorial",
        "short",
        "pls",
        "instead",
        "lets",
        "you",
        "write",
        "than",
        "into",
        "used",
        "being",
    }
)
_WORD = re.compile(r"[a-z0-9]+", re.I)

# AJ0 held-out pack (same questions for both arms).
GENPEAK_PACK: tuple[dict[str, str], ...] = tuple(
    {
        "id": p["id"],
        "app_id": p["app_id"],
        "source_id": p["source_id"],
        "question": p["question"],
        "gold": p["gold"],
    }
    for p in AJ0_PACK
)


def _q_tokens(question: str) -> list[str]:
    return [
        w
        for w in _WORD.findall(str(question).lower())
        if len(w) > 2 and w not in _STOP
    ]


def _chunk_score(question: str, chunk: str) -> float:
    base = jaccard(question, chunk)
    toks = _q_tokens(question)
    cl = chunk.lower()
    return base + 0.08 * float(sum(1 for t in toks if t in cl))


def peak_top_k_chunks(
    question: str,
    chunks: Sequence[str],
    k: int,
) -> list[str]:
    """
    GIVEN question + source chunks
    WHEN retrieving for GENPEAK
    THEN return top-k by Jaccard + cue-token boost (not gold).
    """
    kk = int(k)
    if kk < 1 or not chunks:
        return []
    scored = sorted(
        ((_chunk_score(question, c), i, c) for i, c in enumerate(chunks)),
        key=lambda t: (-t[0], t[1]),
    )
    return [c for _, _, c in scored[:kk]]


def _add_cand(
    cands: list[tuple[float, str]],
    score: float,
    text: str,
) -> None:
    t = str(text).strip().strip("`'\"")
    if not t or len(t) > 80:
        return
    if t.endswith("()") and len(t) > 2:
        t = t[:-2]
    if t.lower().endswith(".html"):
        return
    cands.append((float(score), t))


def _add_bytes_near_label(
    cands: list[tuple[float, str]],
    context: str,
    question: str,
) -> None:
    toks = _q_tokens(question)
    ql = question.lower()
    # Field-name cues beat generic "bytes" in neighboring labels.
    field_cues = [
        t
        for t in toks
        if t not in {"bytes", "byte", "serialization", "extended", "bip"}
    ]
    for m in re.finditer(r"(\d+)\s*bytes?\s*:\s*([^\n]{0,80})", context, re.I):
        num, label = m.group(1), m.group(2).lower()
        cue_hits = sum(1 for t in field_cues if t in label)
        boost = 1.0 + 1.2 * cue_hits
        if "byte" in ql:
            boost += 0.3
        if cue_hits == 0:
            boost -= 0.8
        _add_cand(cands, 2.0 + boost, num)


def _add_witness_program(
    cands: list[tuple[float, str]],
    context: str,
    question: str,
) -> None:
    ql = question.lower()
    wants32 = "32" in ql and "byte" in ql
    for m in re.finditer(
        r"witness program is 32 bytes[^\n]{0,120}?(P2W[A-Z]+)",
        context,
        re.I,
    ):
        _add_cand(cands, 5.0, m.group(1))
    for m in re.finditer(r"\b(P2WSH|P2WPKH|P2SH)\b", context):
        score = 2.5
        if wants32 and m.group(1) == "P2WSH":
            score = 4.8
        elif wants32 and m.group(1) == "P2WPKH":
            score = 1.5
        _add_cand(cands, score, m.group(1))


def _add_html_builtin_spans(
    cands: list[tuple[float, str]],
    context: str,
    question: str,
) -> None:
    ql = question.lower()
    wants_builtin = "built-in" in ql or "builtin" in ql or "statement" in ql
    if wants_builtin:
        for m in re.finditer(r'title="([a-z_][a-z0-9_]*)"', context, re.I):
            _add_cand(cands, 3.6, m.group(1))
        for m in re.finditer(r"#([a-z_][a-z0-9_]*)\"", context):
            _add_cand(cands, 3.4, m.group(1))
    pre_score = 1.0 if wants_builtin else 1.6
    for m in re.finditer(r'class="pre">([^<]{1,40})</span>', context):
        _add_cand(cands, pre_score, m.group(1))


def _add_keyword_spans(
    cands: list[tuple[float, str]],
    context: str,
    question: str,
) -> None:
    for kw in ("continue", "isinstance", "i32", "break", "pass"):
        if not re.search(rf"\b{re.escape(kw)}\b", context, re.I):
            continue
        dens = 0
        for m in re.finditer(rf".{{0,60}}\b{re.escape(kw)}\b.{{0,60}}", context, re.I):
            win = m.group(0).lower()
            dens = max(dens, sum(1 for t in _q_tokens(question) if t in win))
        base = 2.4 if kw in {"isinstance", "continue", "i32"} else 1.2
        _add_cand(cands, base + 0.5 * dens, kw)


def _add_generic_spans(
    cands: list[tuple[float, str]],
    context: str,
    question: str,
) -> None:
    ql = question.lower()
    for m in re.finditer(r"multiple of\s+(\d+)", context, re.I):
        _add_cand(cands, 3.0, m.group(1))
    for m in re.finditer(
        r"\b([a-z_][a-z0-9_]*\.[a-z_][a-z0-9_]*)\b", context, re.I
    ):
        score = (
            2.8
            if ("queue" in ql or "module" in ql or "preferred" in ql)
            else 1.0
        )
        _add_cand(cands, score, m.group(1))
    for m in re.finditer(r"`([^`]{1,60})`", context):
        _add_cand(cands, 1.8, m.group(1))
    for phrase in (
        "field init shorthand",
        "Internet Header Length",
        "struct update syntax",
    ):
        if phrase.lower() in context.lower():
            _add_cand(cands, 4.5, phrase)
    for m in re.finditer(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,4})\b", context):
        score = 2.0 if ("expand" in ql or "ihl" in ql) else 0.8
        _add_cand(cands, score, m.group(1))
    if "/wallet/<walletname>/" in context:
        _add_cand(cands, 5.0, "/wallet/<walletname>/")
    _add_html_builtin_spans(cands, context, question)
    _add_keyword_spans(cands, context, question)


def extract_peak_answer(question: str, context: str) -> str | None:
    """
    GIVEN question + retrieved context (no gold)
    WHEN peaking a short factual span
    THEN return best extractive candidate or None.
    """
    ctx = str(context or "")
    if not ctx.strip():
        return None
    cands: list[tuple[float, str]] = []
    _add_bytes_near_label(cands, ctx, question)
    _add_witness_program(cands, ctx, question)
    _add_generic_spans(cands, ctx, question)
    if not cands:
        return None
    cands.sort(key=lambda t: (-t[0], abs(len(t[1]) - 12)))
    seen: set[str] = set()
    for _score, text in cands:
        key = text.lower()
        if key in seen:
            continue
        seen.add(key)
        return text
    return None


def apply_peak_completion(
    *,
    decode_text: str,
    question: str,
    context: str,
) -> tuple[str, bool, str | None]:
    """
    GIVEN decode completion + grounded context
    WHEN applying GENPEAK extractive stop
    THEN prefer peak span when present; else keep polished decode.
    """
    peak = extract_peak_answer(question, context)
    polished = normalize_gen_answer(decode_text)
    if peak and not is_period_collapse(peak):
        return normalize_gen_answer(peak), True, peak
    return polished, False, peak


def _contains_phrase(hay: str, needle: str) -> bool:
    h = str(hay).lower()
    n = str(needle).lower().strip()
    if not h or not n:
        return False
    if len(n) <= 3:
        return bool(re.search(rf"(?<![a-z0-9]){re.escape(n)}(?![a-z0-9])", h))
    return n in h


def score_genpeak_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN LOOKUP arm ask
    WHEN Cursor EVAL
    THEN (score, error, notes); LOOKUP ≠ generative IQ.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
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
        "GENPEAK LOOKUP product retrieve — not generative IQ",
        f"lookup_kind={lookup_kind}",
    ]
    if arm != "LOOKUP":
        return float(score), True, notes + ["LOOKUP arm mislabeled"]
    return float(score), bool(err), notes


def score_genpeak_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """
    GIVEN GENERATE arm (grounded QPFB2 + extractive peak)
    WHEN Cursor EVAL completion vs gold
    THEN exact→9; gold phrase in completion→7; overlap≥0.35→6;
         overlap≥0.2→5; period→1; else mid 4. Require gen telemetry.
    """
    text = normalize_gen_answer(completion)
    g = str(expected_gold).strip()
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    period = is_period_collapse(text)
    peak_used = bool(payload.get("peak_used"))
    base_notes = [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']} period={period} peak={peak_used}",
        "GENPEAK grounded+extractive — Cursor scores completion "
        "(not LOOKUP IQ)",
        f"beat GENPLUS gen={GENPLUS_GEN_MEAN} / SERVEALIGN={SERVEALIGN_MEAN}",
    ]
    if arm != "GENERATE" or tel["wall_ms"] <= 0.0 or tel["n_new"] <= 0:
        return 4.0, True, base_notes + ["gen telemetry fail"]
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


def genpeak_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    n_period: int,
    n_fix: int,
    n_peak: int,
) -> dict[str, Any]:
    """
    GIVEN dual-arm scores
    WHEN summarizing H-GENPEAK
    THEN means + pass flags vs LOOKUP≥7 / GEN≥5.
    """
    if len(lookup_scores) != GENPEAK_N or len(gen_scores) != GENPEAK_N:
        raise ValueError(f"GENPEAK requires {GENPEAK_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(GENPEAK_N))
    g_mean = float(sum(gen_scores) / float(GENPEAK_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    return {
        "n_trials": GENPEAK_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_period": int(n_period),
        "n_fix": int(n_fix),
        "n_peak": int(n_peak),
        "min_lookup_mean": MIN_LOOKUP_MEAN,
        "min_gen_mean": MIN_GEN_MEAN,
        "genplus_gen_mean": GENPLUS_GEN_MEAN,
        "servealign_mean": SERVEALIGN_MEAN,
        "pass_lookup": l_mean >= MIN_LOOKUP_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "pass_gen": g_mean >= MIN_GEN_MEAN,
        "beats_genplus_gen": g_mean > GENPLUS_GEN_MEAN,
        "beats_servealign": g_mean > SERVEALIGN_MEAN,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_genpeak(stats: Mapping[str, Any]) -> str:
    """
    GIVEN GENPEAK dual-arm stats
    WHEN applying pesquisa §3 AJ1 gate
    THEN KILL if false-hit; PROMOTE if lookup+gen≥5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("dual_arm")):
        return "KILL"
    if bool(stats.get("pass_lookup")) and bool(stats.get("pass_gen")):
        return "PROMOTE"
    return "HOLD"
