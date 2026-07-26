"""Wave AF1 H-CTXULTRA: triple-doc ROLL/SUMCACHE; L_eff↑ vs CTXMAX."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from af_session_ops import AF0_PACK
from ctxmax_ops import TOP_K_SLICES_MAX
from ctxplus_ops import (
    ACTIVE_CAP,
    MIN_LEFF,
    MIN_LEFF_RATIO,
    ctxplus_doc_meta,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "CTXULTRA_ID",
    "CTXULTRA_N",
    "MIN_USABLE",
    "MIN_SOURCES",
    "TOP_K_SLICES_ULTRA",
    "CTXMAX_MEAN_LEFF",
    "CTXULTRA_SECONDARY",
    "CTXULTRA_TERTIARY",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "secondary_for",
    "tertiary_for",
    "ctxultra_doc_meta",
    "score_ctxultra_trial",
    "ctxultra_stats",
    "decide_ctxultra",
]

CTXULTRA_ID = "H-CTXULTRA"
CTXULTRA_N = 10
MIN_USABLE = 7  # pesquisa §5 AF1
MIN_SOURCES = 3
# Deeper than CTXMAX K=5.
TOP_K_SLICES_ULTRA = 7
# Evidence: results/nano-lm/wave-ae/ctxmax_summary.json mean_l_eff
CTXMAX_MEAN_LEFF = 31043.2

# Primary AF0 source_id → secondary / tertiary curated sources.
CTXULTRA_SECONDARY: Mapping[str, str] = {
    "bip-0001": "bip-0032",
    "bitcoin-doc-bips": "bip-0001",
    "rust-book-ch03-02": "rust-book-ch03",
    "python-tutorial-classes": "python-tutorial-datastructures",
    "python-tutorial-control": "python-tutorial-intro",
    "python-tutorial-intro": "python-tutorial-control",
    "rust-book-ch04-01": "rust-book-ch03-02",
    "rust-book-ch05-01": "rust-book-ch04-01",
    "bitcoin-core-readme": "bitcoin-developer-notes",
    "rfc8446": "rfc791",
}

CTXULTRA_TERTIARY: Mapping[str, str] = {
    "bip-0001": "bip-0039",
    "bitcoin-doc-bips": "bitcoin-core-readme",
    "rust-book-ch03-02": "rust-book-ch04-01",
    "python-tutorial-classes": "python-tutorial-intro",
    "python-tutorial-control": "python-tutorial-classes",
    "python-tutorial-intro": "python-tutorial-io",
    "rust-book-ch04-01": "rust-book-ch05-01",
    "rust-book-ch05-01": "rust-book-ch03-02",
    "bitcoin-core-readme": "bitcoin-doc-bips",
    "rfc8446": "rfc8949",
}


def secondary_for(source_id: str) -> str:
    """
    GIVEN primary source_id
    WHEN resolving CTXULTRA secondary
    THEN return secondary curated id (raises if unknown).
    """
    sid = str(source_id)
    if sid not in CTXULTRA_SECONDARY:
        raise KeyError(f"no CTXULTRA secondary for {sid}")
    return str(CTXULTRA_SECONDARY[sid])


def tertiary_for(source_id: str) -> str:
    """
    GIVEN primary source_id
    WHEN resolving CTXULTRA tertiary
    THEN return tertiary curated id (raises if unknown).
    """
    sid = str(source_id)
    if sid not in CTXULTRA_TERTIARY:
        raise KeyError(f"no CTXULTRA tertiary for {sid}")
    return str(CTXULTRA_TERTIARY[sid])


def ctxultra_doc_meta(
    primary_ids: Sequence[int],
    secondary_ids: Sequence[int],
    tertiary_ids: Sequence[int],
    question_ids: Sequence[int],
    *,
    primary_source: str,
    secondary_source: str,
    tertiary_source: str,
    k: int = TOP_K_SLICES_ULTRA,
) -> dict[str, Any]:
    """
    GIVEN three curated docs + question tokens
    WHEN building CTXULTRA context
    THEN triple multi-slice metas with n_sources≥3 and L_eff vs CTXMAX.
    """
    primary = ctxplus_doc_meta(primary_ids, question_ids, k=k)
    secondary = ctxplus_doc_meta(secondary_ids, question_ids, k=k)
    tertiary = ctxplus_doc_meta(tertiary_ids, question_ids, k=k)
    combined_l = (
        int(primary["l_eff"])
        + int(secondary["l_eff"])
        + int(tertiary["l_eff"])
    )
    combined_slices = (
        int(primary["n_slices"])
        + int(secondary["n_slices"])
        + int(tertiary["n_slices"])
    )
    combined_union = (
        int(primary["slice_union"])
        + int(secondary["slice_union"])
        + int(tertiary["slice_union"])
    )
    active = int(primary["sumcache_active"])
    ratio_ok = bool(primary["ratio_ok"]) or (
        float(combined_l) >= float(MIN_LEFF) * float(MIN_LEFF_RATIO)
    )
    return {
        "primary_source": str(primary_source),
        "secondary_source": str(secondary_source),
        "tertiary_source": str(tertiary_source),
        "n_sources": MIN_SOURCES,
        "k_slices": int(k),
        "l_eff": int(combined_l),
        "primary_l_eff": int(primary["l_eff"]),
        "secondary_l_eff": int(secondary["l_eff"]),
        "tertiary_l_eff": int(tertiary["l_eff"]),
        "n_slices": int(combined_slices),
        "primary_slices": int(primary["n_slices"]),
        "secondary_slices": int(secondary["n_slices"]),
        "tertiary_slices": int(tertiary["n_slices"]),
        "slice_union": int(combined_union),
        "sumcache_active": int(active),
        "best_slice_active": int(primary.get("best_slice_active") or 0),
        "ctx_bounded": active <= int(ACTIVE_CAP),
        "l_eff_ok": int(combined_l) >= int(MIN_LEFF),
        "ratio_vs_roll_w": float(primary["ratio_vs_roll_w"]),
        "ratio_ok": bool(ratio_ok),
        "multi_source": True,
        "multi_deeper": True,
        "above_ctxmax_leff": float(combined_l) > float(CTXMAX_MEAN_LEFF),
        "deeper_than_ctxmax_k": int(k) > int(TOP_K_SLICES_MAX),
        "primary": primary,
        "secondary": secondary,
        "tertiary": tertiary,
    }


def score_ctxultra_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    meta: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN CTXULTRA ask + triple-doc ctx meta
    WHEN scoring HITL
    THEN (score, error, notes, usable).
    usable ⇒ score≥8 ∧ n_sources≥3 ∧ L_eff/bounded/slices.
    """
    from semwrap_ops import score_semwrap_trial

    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=completion,
        expected_gold=expected_gold,
        lookup_kind=lookup_kind,
    )
    n_src = int(meta.get("n_sources") or 0)
    ctx_ok = bool(meta.get("l_eff_ok")) and bool(meta.get("ratio_ok"))
    ctx_ok = ctx_ok and bool(meta.get("ctx_bounded"))
    ctx_ok = ctx_ok and n_src >= MIN_SOURCES
    slices_ok = int(meta.get("n_slices") or 0) >= 1
    usable = (not err) and score >= 8.0 and ctx_ok and slices_ok
    notes = list(notes) + [
        (
            f"sources={n_src} L_eff={meta.get('l_eff')} "
            f"slices={meta.get('n_slices')} k={meta.get('k_slices')} "
            f"active={meta.get('sumcache_active')} "
            f"trio={meta.get('primary_source')}+"
            f"{meta.get('secondary_source')}+"
            f"{meta.get('tertiary_source')}"
        ),
        (
            "CTXULTRA triple-doc ROLL+SUMCACHE — not STREAM / naive CTX"
            if ctx_ok and slices_ok
            else "FIX: triple-doc/ctx gate failed"
        ),
    ]
    if (not ctx_ok or not slices_ok) and not err:
        return score, True, notes, False
    return score, err, notes, usable


def ctxultra_stats(
    scores: Sequence[float],
    errors: Sequence[bool],
    usables: Sequence[bool],
    *,
    n_true_hit: int,
    n_false_hit: int,
    n_miss: int,
    mean_l_eff: float,
    mean_active: float,
    mean_slices: float,
    mean_sources: float,
    n_multi_source: int,
    n_fix: int,
) -> dict[str, Any]:
    """
    GIVEN 10 CTXULTRA scores + ctx means
    WHEN summarizing AF1
    THEN quality + usable≥7 + L_eff↑ vs CTXMAX + triple-doc.
    """
    if len(scores) != CTXULTRA_N or len(errors) != CTXULTRA_N:
        raise ValueError(
            f"CTXULTRA requires exactly {CTXULTRA_N} scores/errors"
        )
    if len(usables) != CTXULTRA_N:
        raise ValueError(
            f"CTXULTRA requires exactly {CTXULTRA_N} usable flags"
        )
    mean = float(sum(scores) / float(CTXULTRA_N))
    n_err = int(sum(1 for e in errors if e))
    n_usable = int(sum(1 for u in usables if u))
    return {
        "n_trials": CTXULTRA_N,
        "mean": mean,
        "n_errors": n_err,
        "n_usable": n_usable,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "n_miss": int(n_miss),
        "mean_l_eff": float(mean_l_eff),
        "mean_active": float(mean_active),
        "mean_slices": float(mean_slices),
        "mean_sources": float(mean_sources),
        "n_multi_source": int(n_multi_source),
        "n_fix": int(n_fix),
        "ctxmax_mean_leff": float(CTXMAX_MEAN_LEFF),
        "min_usable": MIN_USABLE,
        "min_sources": MIN_SOURCES,
        "top_k": TOP_K_SLICES_ULTRA,
        "pass_usable": n_usable >= MIN_USABLE,
        "pass_multi_source": float(mean_sources) >= float(MIN_SOURCES)
        and int(n_multi_source) >= MIN_USABLE,
        "pass_leff_up": float(mean_l_eff) > float(CTXMAX_MEAN_LEFF),
        "pass_active": float(mean_active) <= float(ACTIVE_CAP),
        "pass_slices": float(mean_slices) >= float(TOP_K_SLICES_ULTRA),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "pack_ids": [p["id"] for p in AF0_PACK],
    }


def decide_ctxultra(stats: Mapping[str, Any]) -> str:
    """
    GIVEN CTXULTRA stats
    WHEN applying pesquisa §5 AF1 gate
    THEN PROMOTE if usable≥7 ∧ L_eff↑ ∧ triple-doc ∧ quality ∧ no false-hit;
         HOLD if no false-hit but soft-fail; KILL if false-hit.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    ok = (
        bool(stats.get("pass_usable"))
        and bool(stats.get("pass_multi_source"))
        and bool(stats.get("pass_leff_up"))
        and bool(stats.get("pass_active"))
        and bool(stats.get("pass_slices"))
        and bool(stats.get("pass_quality"))
    )
    if ok:
        return "PROMOTE"
    return "HOLD"
