"""Wave AS7 H-NANOGEN3: ablated DECODE lift vs H-NANOGEN2 4.3."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from as_session_ops import AS0_NANOGEN3_HYPOTHESIS
from nanogen2_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_bank_grounded_short,
    gold_in_context,
    nanogen2_stats,
    score_nanogen2_gen,
    score_nanogen2_lookup,
)
from nanogen_ops import NANOGEN_N, NANOGEN_PACK, decide_nanogen

__all__ = [
    "NANOGEN3_ID",
    "NANOGEN3_N",
    "NANOGEN3_PACK",
    "NANOGEN3_THESIS",
    "NANOGEN3_HYPOTHESIS",
    "PARENT_NANOGEN2_ABLATED",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "gold_in_context",
    "apply_bank_grounded_short",
    "score_nanogen3_lookup",
    "score_nanogen3_gen",
    "nanogen3_stats",
    "decide_nanogen3",
]

NANOGEN3_ID = "H-NANOGEN3"
NANOGEN3_N = NANOGEN_N
NANOGEN3_PACK = NANOGEN_PACK  # same pack → fair lift vs H-NANOGEN2
NANOGEN3_HYPOTHESIS = AS0_NANOGEN3_HYPOTHESIS
PARENT_NANOGEN2_ABLATED = 4.3
NANOGEN3_THESIS = (
    "Ablated DECODE lift vs H-NANOGEN2 4.3 via bank-grounded short + "
    "ASKABSTAIN refuse-junk on default ask path; PROMOTE iff ablated≥5.0 "
    "else HOLD (peak/bank compare only)"
)


def score_nanogen3_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_nanogen2_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("NANOGEN2 LOOKUP", "NANOGEN3 LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_nanogen3_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """
    GIVEN DECODE/GENERATE completion
    WHEN scoring AS7 gate
    THEN bank-grounded / peak assists excluded from ablated true-gen.
    """
    score, err, notes = score_nanogen2_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=peak_ablated,
    )
    notes = [n.replace("NANOGEN2", "NANOGEN3") for n in notes]
    return float(score), bool(err), notes


def nanogen3_stats(
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
    WHEN summarizing H-NANOGEN3
    THEN gate on ablated gen_mean; vs NANOGEN2 4.3; peak/bank compare-only.
    """
    base = nanogen2_stats(
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
    base["parent_nanogen2_ablated"] = PARENT_NANOGEN2_ABLATED
    base["beats_nanogen2_ablated"] = (
        float(base["gen_mean"]) > PARENT_NANOGEN2_ABLATED
    )
    # Keep parent_nanogen_ablated key for decide_nanogen compatibility notes
    base["parent_nanogen_ablated"] = PARENT_NANOGEN2_ABLATED
    base["beats_nanogen_ablated"] = base["beats_nanogen2_ablated"]
    base["hypothesis"] = NANOGEN3_HYPOTHESIS
    return base


def decide_nanogen3(stats: Mapping[str, Any]) -> str:
    """
    GIVEN NANOGEN3 dual-arm + ablation stats
    WHEN applying pesquisa §5 AS7 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    """
    return decide_nanogen(stats)
