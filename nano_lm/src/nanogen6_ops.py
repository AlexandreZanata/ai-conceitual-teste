"""Wave AV3 H-NANOGEN6: refuse-or-continue; span-fallback ≠ gen IQ."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from abstain_ops import is_junk_decode
from asksmart_ops import is_period_collapse
from av_session_ops import AV0_NANOGEN6_HYPOTHESIS, AV0_TRUE_GEN_JUDGE
from genbase_ops import normalize_gen_answer
from nanogen5_ops import (
    MIN_LOOKUP_MEAN,
    NANOGEN5_N,
    NANOGEN5_PACK,
    _continuation_after_prefix,
    _f1_to_score,
    apply_bank_grounded_short,
    apply_snippet_prefix_decode,
    continuation_is_gibberish,
    is_usable_gen_span,
    nanogen5_stats,
    score_nanogen5_lookup,
    select_snippet_span,
    short_answer_token_f1,
)
from nanogen_ops import decide_nanogen

__all__ = [
    "NANOGEN6_ID",
    "NANOGEN6_N",
    "NANOGEN6_PACK",
    "NANOGEN6_THESIS",
    "NANOGEN6_HYPOTHESIS",
    "PARENT_NANOGEN5_STRICT",
    "MIN_LOOKUP_MEAN",
    "MIN_TRUE_CONTINUE_MEAN",
    "TRUE_GEN_JUDGE",
    "CONTINUE_KINDS",
    "apply_bank_grounded_short",
    "apply_snippet_prefix_decode",
    "select_snippet_span",
    "short_answer_token_f1",
    "is_usable_gen_span",
    "continuation_is_gibberish",
    "apply_refuse_or_continue",
    "score_nanogen6_lookup",
    "score_nanogen6_gen",
    "nanogen6_stats",
    "decide_nanogen6",
]

NANOGEN6_ID = "H-NANOGEN6"
NANOGEN6_N = NANOGEN5_N
NANOGEN6_PACK = NANOGEN5_PACK  # fair compare vs archived NANOGEN5 STRICT 5.5
NANOGEN6_HYPOTHESIS = AV0_NANOGEN6_HYPOTHESIS
PARENT_NANOGEN5_STRICT = 5.5
# Same numeric floor as NANOGEN5, but span-fallback wins score 4.0 (no gen credit).
MIN_TRUE_CONTINUE_MEAN = 5.5
TRUE_GEN_JUDGE = dict(AV0_TRUE_GEN_JUDGE)
CONTINUE_KINDS = frozenset({"true_continue", "span_fallback", "abstain"})
NANOGEN6_THESIS = (
    "Ablated DECODE refuse-or-continue: score only true novel readable "
    "continue; truncate-to-span = PEAK/LOOKUP fallback (zero gen credit); "
    "gibberish → ABSTAIN; not NANOGEN5 5.5 truncate clone; "
    "bar = true_continue_ablated≥5.5 else HOLD"
)


def apply_refuse_or_continue(
    *,
    text: str,
    prefix: str = "",
) -> tuple[str, str, bool, bool]:
    """
    GIVEN decode text (+ optional snippet prefix)
    WHEN applying refuse-or-continue law
    THEN return (out, kind, truncated, refuse)
         kind ∈ {true_continue, span_fallback, abstain}.
    """
    cleaned = normalize_gen_answer(text)
    seed = normalize_gen_answer(prefix).strip()
    if not cleaned or is_period_collapse(cleaned):
        return cleaned, "abstain", False, True
    if continuation_is_gibberish(text=cleaned, prefix=seed):
        if seed and is_usable_gen_span(seed):
            return seed, "span_fallback", True, False
        return cleaned, "abstain", False, True
    if not is_usable_gen_span(cleaned):
        if seed and is_usable_gen_span(seed):
            return seed, "span_fallback", True, False
        return cleaned, "abstain", False, True
    if seed:
        cont = _continuation_after_prefix(cleaned, seed)
        if not cont.strip():
            # Output is retrieved span only — extractive, not generative.
            return cleaned, "span_fallback", True, False
    return cleaned, "true_continue", False, False


def score_nanogen6_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_nanogen5_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("NANOGEN5 LOOKUP", "NANOGEN6 LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_nanogen6_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN DECODE/GENERATE completion
    WHEN scoring AV3 true-gen judge
    THEN span-fallback / truncate → 4.0 (≠ gen IQ);
         true continue scored by short-answer F1/HITL;
         gold-substring alone insufficient.
    """
    notes = ["NANOGEN6 true-gen judge (refuse-or-continue)"]
    if peak_ablated and bool(payload.get("bank_grounded")):
        return (
            4.0,
            True,
            notes
            + [
                "bank-gold rewrite is compare only",
                "excluded from true_continue gate (anti-FP)",
            ],
        )
    if peak_ablated and bool(payload.get("peak_used")):
        return (
            4.0,
            True,
            notes
            + [
                "peak overlay is compare only",
                "excluded from true_continue gate (anti-FP)",
            ],
        )
    kind = str(payload.get("continue_kind") or "")
    if bool(payload.get("span_fallback")) or kind == "span_fallback":
        return (
            4.0,
            True,
            notes
            + [
                "span-fallback ≠ gen IQ (PEAK/LOOKUP credit only)",
                "not a NANOGEN5 truncate-bar clone win",
            ],
        )
    if (
        bool(payload.get("abstained"))
        or kind == "abstain"
        or str(payload.get("product_mode") or "") == "ABSTAIN"
    ):
        return (
            4.0,
            True,
            notes + ["refuse-or-continue: ABSTAIN (no gen credit)"],
        )
    if bool(payload.get("gibberish_tail_truncated")):
        return (
            4.0,
            True,
            notes + ["truncated-to-span forbidden as gen credit"],
        )
    text = normalize_gen_answer(completion)
    if is_junk_decode(text) or not is_usable_gen_span(text):
        return 4.0, True, notes + ["usable true_continue required"]
    if float(payload.get("wall_ms") or 0.0) <= 0.0:
        return 4.0, True, notes + ["wall_ms mandatory but insufficient alone"]
    if int(payload.get("n_new") or 0) <= 0:
        return 4.0, True, notes + ["n_new mandatory but insufficient alone"]
    f1 = short_answer_token_f1(text, expected_gold)
    g = str(expected_gold or "").strip().lower()
    buried = bool(g) and g in text.lower() and f1 < 0.35
    if buried:
        return (
            4.0,
            True,
            notes
            + [
                f"gold-substring alone insufficient (F1={f1:.2f})",
                "true_continue requires short-answer F1/HITL",
            ],
        )
    score, err, msg = _f1_to_score(f1)
    if bool(payload.get("snippet_prefix")):
        notes.append("snippet-prefix seed + novel continue")
    notes.append(msg)
    return float(score), bool(err), notes


def nanogen6_stats(
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
    n_span_fallback: int = 0,
    n_true_continue: int = 0,
) -> dict[str, Any]:
    """
    GIVEN dual-arm + true_continue scores (n=10)
    WHEN summarizing H-NANOGEN6
    THEN gate on true_continue_ablated≥5.5; span-fallback wins = 0 gen credit.
    """
    base = nanogen5_stats(
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
        n_snippet_prefix=n_snippet_prefix,
        n_gibberish_truncated=n_span_fallback,
    )
    g_mean = float(base["gen_mean"])
    base["min_gen_mean"] = MIN_TRUE_CONTINUE_MEAN
    base["pass_gen"] = g_mean >= MIN_TRUE_CONTINUE_MEAN
    base["parent_nanogen5_strict"] = PARENT_NANOGEN5_STRICT
    base["beats_nanogen5_true_continue"] = g_mean > PARENT_NANOGEN5_STRICT
    base["n_span_fallback"] = int(n_span_fallback)
    base["n_true_continue"] = int(n_true_continue)
    base["span_fallback_neq_gen"] = True
    base["true_gen_judge"] = dict(TRUE_GEN_JUDGE)
    base["hypothesis"] = NANOGEN6_HYPOTHESIS
    # Anti-clone: if all gen credit came from span-fallback, cannot PROMOTE.
    if int(n_span_fallback) > 0 and int(n_true_continue) == 0:
        base["pass_gen"] = False
        base["peak_only_lift"] = True
    return base


def decide_nanogen6(stats: Mapping[str, Any]) -> str:
    """
    GIVEN NANOGEN6 dual-arm + true_continue ablation stats
    WHEN applying pesquisa §5 AV3 gate
    THEN KILL if false-hit; PROMOTE iff lookup+true_continue≥5.5; else HOLD.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    if not bool(stats.get("span_fallback_neq_gen")):
        return "KILL"
    return decide_nanogen(stats)
