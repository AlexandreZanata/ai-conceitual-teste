"""Wave AT3 H-NANOGEN4: ablated DECODE via retrieved-snippet prefix."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from at_session_ops import AT0_NANOGEN4_HYPOTHESIS
from genbase_ops import extract_genbase_answer, normalize_gen_answer
from genplus_ops import is_period_collapse
from nanogen3_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_bank_grounded_short,
    gold_in_context,
    nanogen3_stats,
    score_nanogen3_gen,
    score_nanogen3_lookup,
)
from nanogen_ops import NANOGEN_N, NANOGEN_PACK, decide_nanogen

__all__ = [
    "NANOGEN4_ID",
    "NANOGEN4_N",
    "NANOGEN4_PACK",
    "NANOGEN4_THESIS",
    "NANOGEN4_HYPOTHESIS",
    "PARENT_NANOGEN3_ABLATED",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "SNIPPET_MAX_CHARS",
    "CONTINUE_MAX_CHARS",
    "gold_in_context",
    "apply_bank_grounded_short",
    "select_snippet_span",
    "apply_snippet_prefix_decode",
    "score_nanogen4_lookup",
    "score_nanogen4_gen",
    "nanogen4_stats",
    "decide_nanogen4",
]

NANOGEN4_ID = "H-NANOGEN4"
NANOGEN4_N = NANOGEN_N
NANOGEN4_PACK = NANOGEN_PACK  # same pack → fair lift vs H-NANOGEN3
NANOGEN4_HYPOTHESIS = AT0_NANOGEN4_HYPOTHESIS
PARENT_NANOGEN3_ABLATED = 4.3
SNIPPET_MAX_CHARS = 96
CONTINUE_MAX_CHARS = 48
NANOGEN4_THESIS = (
    "Ablated DECODE lift vs H-NANOGEN3 4.3 via retrieved-snippet prefix "
    "conditioning (student continues ≤N; no bank-gold rewrite); PROMOTE "
    "iff ablated≥5.0 else HOLD (peak/bank compare only)"
)


def select_snippet_span(*, question: str, context: str) -> str | None:
    """
    GIVEN question + retrieved RAG context (no gold arg)
    WHEN selecting a short contiguous seed span
    THEN return normalized snippet or None.
    """
    span = extract_genbase_answer(question, context)
    if not span:
        return None
    text = normalize_gen_answer(span).strip()
    if not text or is_period_collapse(text):
        return None
    if len(text) > SNIPPET_MAX_CHARS:
        text = text[:SNIPPET_MAX_CHARS].rstrip()
    return text or None


def apply_snippet_prefix_decode(
    *,
    decode_text: str,
    question: str,
    context: str,
) -> tuple[str, bool, str]:
    """
    GIVEN ablated decode + retrieved context
    WHEN seeding with RAG snippet prefix (not bank gold)
    THEN return (text, used, prefix); student continue capped.
    """
    decoded = normalize_gen_answer(decode_text)
    span = select_snippet_span(question=question, context=context)
    if not span:
        return decoded, False, ""
    span_l = span.lower()
    dec_l = decoded.lower()
    if span_l and (span_l == dec_l or (len(span_l) > 2 and span_l in dec_l)):
        return decoded, False, ""
    cont = decoded[:CONTINUE_MAX_CHARS].strip()
    if cont and cont.lower() != span_l and span_l not in cont.lower():
        if not is_period_collapse(cont):
            return f"{span} {cont}".strip(), True, span
    return span, True, span


def score_nanogen4_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_nanogen3_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("NANOGEN3 LOOKUP", "NANOGEN4 LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_nanogen4_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN DECODE/GENERATE completion
    WHEN scoring AT3 gate
    THEN bank-gold / peak excluded; snippet-prefix allowed on ablated.
    """
    if peak_ablated and bool(payload.get("bank_grounded")):
        return (
            4.0,
            True,
            [
                "NANOGEN4 ablated — bank-gold rewrite is compare only",
                "excluded from ablated true-gen gate (anti-FP)",
            ],
        )
    if peak_ablated and bool(payload.get("peak_used")):
        return (
            4.0,
            True,
            [
                "NANOGEN4 ablated — peak overlay is compare only",
                "excluded from ablated true-gen gate (anti-FP)",
            ],
        )
    clean = dict(payload)
    clean["bank_grounded"] = False
    clean["peak_used"] = False
    score, err, notes = score_nanogen3_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=clean,
        peak_ablated=peak_ablated,
    )
    if bool(payload.get("snippet_prefix")):
        notes = [
            "NANOGEN4 snippet-prefix seed (RAG span + student continue)",
            *notes,
        ]
    notes = [n.replace("NANOGEN3", "NANOGEN4") for n in notes]
    return float(score), bool(err), notes


def nanogen4_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    gen_peak_scores: Sequence[float],
    gen_bank_scores: Sequence[float],
    n_true_hit: int,
    n_false_hit: int,
    n_period: int,
    n_fix: int,
    n_peak: int,
    n_bank_grounded: int,
    n_abstain: int,
    n_snippet_prefix: int = 0,
) -> dict[str, Any]:
    """
    GIVEN dual-arm + peak/bank/snippet stats (n=10)
    WHEN summarizing H-NANOGEN4
    THEN gate on ablated gen_mean; vs NANOGEN3 4.3; peak/bank compare-only.
    """
    base = nanogen3_stats(
        lookup_scores=lookup_scores,
        lookup_errors=lookup_errors,
        gen_scores=gen_scores,
        gen_errors=gen_errors,
        gen_peak_scores=gen_peak_scores,
        gen_bank_scores=gen_bank_scores,
        n_true_hit=n_true_hit,
        n_false_hit=n_false_hit,
        n_period=n_period,
        n_fix=n_fix,
        n_peak=n_peak,
        n_bank_grounded=n_bank_grounded,
        n_abstain=n_abstain,
    )
    base["parent_nanogen3_ablated"] = PARENT_NANOGEN3_ABLATED
    base["beats_nanogen3_ablated"] = (
        float(base["gen_mean"]) > PARENT_NANOGEN3_ABLATED
    )
    base["parent_nanogen_ablated"] = PARENT_NANOGEN3_ABLATED
    base["beats_nanogen_ablated"] = base["beats_nanogen3_ablated"]
    base["n_snippet_prefix"] = int(n_snippet_prefix)
    base["hypothesis"] = NANOGEN4_HYPOTHESIS
    return base


def decide_nanogen4(stats: Mapping[str, Any]) -> str:
    """
    GIVEN NANOGEN4 dual-arm + ablation stats
    WHEN applying pesquisa §5 AT3 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    """
    return decide_nanogen(stats)
