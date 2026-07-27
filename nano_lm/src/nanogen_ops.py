"""Wave AQ6 H-NANOGEN: ablated DECODE on held-out + paraphrase."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ap_session_ops import AP0_PACK
from aq_session_ops import AQ0_PARA_PACK
from genbase_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    apply_genbase_peak,
    chunk_doc,
    decide_genbase,
    genbase_stats,
    genbase_top_k_chunks,
    score_genbase_gen,
    score_genbase_lookup,
)

__all__ = [
    "NANOGEN_ID",
    "NANOGEN_N",
    "NANOGEN_PACK",
    "NANOGEN_THESIS",
    "MIN_LOOKUP_MEAN",
    "MIN_GEN_MEAN",
    "chunk_doc",
    "genbase_top_k_chunks",
    "apply_genbase_peak",
    "score_nanogen_lookup",
    "score_nanogen_gen",
    "nanogen_stats",
    "decide_nanogen",
]

NANOGEN_ID = "H-NANOGEN"
NANOGEN_N = 10
NANOGEN_THESIS = (
    "North-star generative eval: ablated DECODE on held-out+paraphrase; "
    "mean ≥ 5.0 → PROMOTE else HOLD (peak compare only)"
)


def _held_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for p in AP0_PACK[:5]:
        rows.append(
            {
                "id": str(p["id"]),
                "app_id": str(p["app_id"]),
                "source_id": str(p["source_id"]),
                "question": str(p["question"]),
                "gold": str(p["gold"]),
                "kind": "held-out",
            }
        )
    return rows


def _para_rows() -> list[dict[str, str]]:
    rows: list[dict[str, str]] = []
    for p in AQ0_PARA_PACK:
        if len(rows) >= 5:
            break
        sid = str(p["source_id"])
        # Skip bank-only synthetic ids (no curated blob for peak context).
        if ":" in sid and not sid.startswith("http"):
            continue
        rows.append(
            {
                "id": str(p["id"]),
                "app_id": "paraphrase",
                "source_id": sid,
                "question": str(p["paraphrase"]),
                "gold": str(p["gold"]),
                "kind": "paraphrase",
                "parent_question": str(p["parent_question"]),
            }
        )
    if len(rows) != 5:
        raise ValueError(f"need 5 curated paraphrases, got {len(rows)}")
    return rows


NANOGEN_PACK: tuple[dict[str, str], ...] = tuple(_held_rows() + _para_rows())


def score_nanogen_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str]]:
    """LOOKUP arm — product retrieve ≠ generative IQ."""
    score, err, notes = score_genbase_lookup(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
        payload=payload,
    )
    notes = [n.replace("GENBASE LOOKUP", "NANOGEN LOOKUP") for n in notes]
    return float(score), bool(err), notes


def score_nanogen_gen(
    *,
    completion: str,
    expected_gold: str,
    payload: Mapping[str, Any],
    peak_ablated: bool,
) -> tuple[float, bool, list[str]]:
    """Ablated GENERATE/DECODE gate — peak compare excluded from PROMOTE."""
    score, err, notes = score_genbase_gen(
        completion=completion,
        expected_gold=expected_gold,
        payload=payload,
        peak_ablated=peak_ablated,
    )
    notes = [n.replace("GENBASE", "NANOGEN") for n in notes]
    return float(score), bool(err), notes


def nanogen_stats(
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
    GIVEN dual-arm + peak ablation scores (n=10)
    WHEN summarizing H-NANOGEN
    THEN gate on ablated gen_mean; log peak_mean for anti-FP.
    """
    return genbase_stats(
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


def decide_nanogen(stats: Mapping[str, Any]) -> str:
    """
    GIVEN NANOGEN dual-arm + ablation stats
    WHEN applying pesquisa §5 AQ6 gate
    THEN KILL if false-hit; PROMOTE iff lookup+ablated gen≥5; else HOLD.
    """
    return decide_genbase(stats)
