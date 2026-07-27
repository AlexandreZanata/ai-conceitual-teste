"""Wave AR5 H-NANOGEN2: ablated DECODE lift vs H-NANOGEN 4.0."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ar_session_ops import AR0_NANOGEN2_HYPOTHESIS
from genplus_ops import normalize_gen_answer
from nanogen_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    NANOGEN_N,
    NANOGEN_PACK,
    decide_nanogen,
    nanogen_stats,
    score_nanogen_gen,
    score_nanogen_lookup,
)

__all__ = [
    "NANOGEN2_ID",
    "NANOGEN2_N",
    "NANOGEN2_PACK",
    "NANOGEN2_THESIS",
    "NANOGEN2_HYPOTHESIS",
    "PARENT_NANOGEN_ABLATED",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "gold_in_context",
    "apply_bank_grounded_short",
    "score_nanogen2_lookup",
    "score_nanogen2_gen",
    "nanogen2_stats",
    "decide_nanogen2",
]

NANOGEN2_ID = "H-NANOGEN2"
NANOGEN2_N = NANOGEN_N
NANOGEN2_PACK = NANOGEN_PACK  # same pack → fair lift vs H-NANOGEN
NANOGEN2_HYPOTHESIS = AR0_NANOGEN2_HYPOTHESIS
PARENT_NANOGEN_ABLATED = 4.0
NANOGEN2_THESIS = (
    "Ablated DECODE lift vs H-NANOGEN 4.0 via bank-grounded short + "
    "ABSTAIN on junk; PROMOTE iff ablated≥5.0 else HOLD (peak/bank compare only)"
)


def gold_in_context(*, gold: str, context: str) -> bool:
    """
    GIVEN bank/expected gold + retrieved context
    WHEN checking bank-grounded eligibility
    THEN True iff normalized gold appears in context.
    """
    g = normalize_gen_answer(gold).strip().lower()
    ctx = str(context or "").lower()
    if not g or not ctx:
        return False
    if len(g) <= 3:
        return f" {g} " in f" {ctx} " or ctx.strip() == g
    return g in ctx


def apply_bank_grounded_short(
    *,
    decode_text: str,
    context: str,
    bank_gold: str,
) -> tuple[str, bool]:
    """
    GIVEN ablated decode + context + bank gold
    WHEN gold is grounded in context and decode misses gold
    THEN emit short bank-grounded continuation (compare/product assist).
    """
    gold = normalize_gen_answer(bank_gold)
    decoded = normalize_gen_answer(decode_text)
    if not gold or not gold_in_context(gold=gold, context=context):
        return decoded, False
    g_low = gold.lower()
    d_low = decoded.lower()
    if d_low == g_low or (len(g_low) > 3 and g_low in d_low):
        return decoded, False
    return gold, True


def score_nanogen2_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_nanogen_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("NANOGEN LOOKUP", "NANOGEN2 LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_nanogen2_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN DECODE/GENERATE completion
    WHEN scoring AR5 gate
    THEN bank-grounded / peak assists excluded from ablated true-gen.
    """
    if peak_ablated and bool(payload.get("bank_grounded")):
        tel = payload
        notes = [
            "NANOGEN2 ablated — bank-grounded short is compare/product only",
            "excluded from ablated true-gen gate (anti-FP)",
            f"mode={tel.get('mode')} wall_ms={tel.get('wall_ms')} "
            f"n_new={tel.get('n_new')}",
        ]
        return 4.0, True, notes
    score, err, notes = score_nanogen_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=peak_ablated,
    )
    notes = [n.replace("NANOGEN", "NANOGEN2") for n in notes]
    return float(score), bool(err), notes


def nanogen2_stats(
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
) -> dict[str, Any]:
    """
    GIVEN dual-arm + peak/bank compare scores (n=10)
    WHEN summarizing H-NANOGEN2
    THEN gate on ablated gen_mean; bank/peak compare-only; vs NANOGEN 4.0.
    """
    base = nanogen_stats(
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
    if len(gen_bank_scores) != NANOGEN2_N:
        raise ValueError(f"NANOGEN2 requires {NANOGEN2_N} bank scores")
    bank_mean = float(sum(gen_bank_scores) / float(NANOGEN2_N))
    base["gen_bank_mean"] = bank_mean
    base["n_bank_grounded"] = int(n_bank_grounded)
    base["n_abstain"] = int(n_abstain)
    base["parent_nanogen_ablated"] = PARENT_NANOGEN_ABLATED
    base["beats_nanogen_ablated"] = (
        float(base["gen_mean"]) > PARENT_NANOGEN_ABLATED
    )
    base["hypothesis"] = NANOGEN2_HYPOTHESIS
    return base


def decide_nanogen2(stats: Mapping[str, Any]) -> str:
    """
    GIVEN NANOGEN2 dual-arm + ablation stats
    WHEN applying pesquisa §5 AR5 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    """
    return decide_nanogen(stats)
