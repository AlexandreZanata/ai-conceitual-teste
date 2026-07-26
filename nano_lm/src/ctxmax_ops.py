"""Wave AE1 H-CTXMAX: multi-doc ROLL/SUMCACHE; L_eff↑ vs CTXPLUS."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ae_session_ops import AE0_PACK
from ctxplus_ops import (
    ACTIVE_CAP,
    MIN_LEFF,
    MIN_LEFF_RATIO,
    TOP_K_SLICES,
    ctxplus_doc_meta,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "CTXMAX_ID",
    "CTXMAX_N",
    "MIN_USABLE",
    "MIN_SOURCES",
    "TOP_K_SLICES_MAX",
    "CTXPLUS_MEAN_LEFF",
    "CTXMAX_SECONDARY",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "secondary_for",
    "ctxmax_doc_meta",
    "score_ctxmax_trial",
    "ctxmax_stats",
    "decide_ctxmax",
]

CTXMAX_ID = "H-CTXMAX"
CTXMAX_N = 10
MIN_USABLE = 7  # pesquisa §5 AE1
MIN_SOURCES = 2
# Deeper than CTXPLUS K=3.
TOP_K_SLICES_MAX = 5
# Evidence: results/nano-lm/wave-ac/ctxplus_summary.json mean_l_eff
CTXPLUS_MEAN_LEFF = 20522.6

# Primary AE0 source_id → secondary curated source (multi-doc).
CTXMAX_SECONDARY: Mapping[str, str] = {
    "bip-0032": "bip-0039",
    "bip-0039": "bip-0032",
    "bip-0340": "bip-0141",
    "python-tutorial-datastructures": "python-tutorial-classes",
    "rust-book-ch03": "rust-book-ch03-02",
    "python-tutorial-io": "python-tutorial-intro",
    "bitcoin-rest": "bitcoin-json-rpc",
    "bitcoin-json-rpc": "bitcoin-rest",
    "rfc791": "rfc8446",
    "bip-0141": "bip-0340",
}


def secondary_for(source_id: str) -> str:
    """
    GIVEN primary source_id
    WHEN resolving CTXMAX pair
    THEN return secondary curated id (raises if unknown).
    """
    sid = str(source_id)
    if sid not in CTXMAX_SECONDARY:
        raise KeyError(f"no CTXMAX secondary for {sid}")
    return str(CTXMAX_SECONDARY[sid])


def ctxmax_doc_meta(
    primary_ids: Sequence[int],
    secondary_ids: Sequence[int],
    question_ids: Sequence[int],
    *,
    primary_source: str,
    secondary_source: str,
    k: int = TOP_K_SLICES_MAX,
) -> dict[str, Any]:
    """
    GIVEN two curated docs + question tokens
    WHEN building CTXMAX context
    THEN dual multi-slice metas with n_sources≥2 and L_eff vs CTXPLUS.
    """
    primary = ctxplus_doc_meta(primary_ids, question_ids, k=k)
    secondary = ctxplus_doc_meta(secondary_ids, question_ids, k=k)
    combined_l = int(primary["l_eff"]) + int(secondary["l_eff"])
    combined_slices = int(primary["n_slices"]) + int(secondary["n_slices"])
    combined_union = int(primary["slice_union"]) + int(secondary["slice_union"])
    active = int(primary["sumcache_active"])
    ratio_ok = bool(primary["ratio_ok"]) or (
        float(combined_l) >= float(MIN_LEFF) * float(MIN_LEFF_RATIO)
    )
    return {
        "primary_source": str(primary_source),
        "secondary_source": str(secondary_source),
        "n_sources": MIN_SOURCES,
        "k_slices": int(k),
        "l_eff": int(combined_l),
        "primary_l_eff": int(primary["l_eff"]),
        "secondary_l_eff": int(secondary["l_eff"]),
        "n_slices": int(combined_slices),
        "primary_slices": int(primary["n_slices"]),
        "secondary_slices": int(secondary["n_slices"]),
        "slice_union": int(combined_union),
        "sumcache_active": int(active),
        "best_slice_active": int(primary.get("best_slice_active") or 0),
        "ctx_bounded": active <= int(ACTIVE_CAP),
        "l_eff_ok": int(combined_l) >= int(MIN_LEFF),
        "ratio_vs_roll_w": float(primary["ratio_vs_roll_w"]),
        "ratio_ok": bool(ratio_ok),
        "multi_source": True,
        "multi_deeper": bool(primary.get("multi_deeper"))
        or bool(secondary.get("multi_deeper")),
        "above_ctxplus_leff": float(combined_l) > float(CTXPLUS_MEAN_LEFF),
        "deeper_than_ctxplus_k": int(k) > int(TOP_K_SLICES),
        "primary": primary,
        "secondary": secondary,
    }


def score_ctxmax_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    meta: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN CTXMAX ask + multi-doc ctx meta
    WHEN scoring HITL
    THEN (score, error, notes, usable).
    usable ⇒ score≥8 ∧ n_sources≥2 ∧ L_eff/bounded/slices.
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
            f"pair={meta.get('primary_source')}+{meta.get('secondary_source')}"
        ),
        (
            "CTXMAX multi-doc ROLL+SUMCACHE — not STREAM / naive CTX"
            if ctx_ok and slices_ok
            else "FIX: multi-doc/ctx gate failed"
        ),
    ]
    if (not ctx_ok or not slices_ok) and not err:
        return score, True, notes, False
    return score, err, notes, usable


def ctxmax_stats(
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
    GIVEN 10 CTXMAX scores + ctx means
    WHEN summarizing AE1
    THEN quality + usable≥7 + L_eff↑ vs CTXPLUS + multi-doc.
    """
    if len(scores) != CTXMAX_N or len(errors) != CTXMAX_N:
        raise ValueError(f"CTXMAX requires exactly {CTXMAX_N} scores/errors")
    if len(usables) != CTXMAX_N:
        raise ValueError(f"CTXMAX requires exactly {CTXMAX_N} usable flags")
    mean = float(sum(scores) / float(CTXMAX_N))
    n_err = int(sum(1 for e in errors if e))
    n_usable = int(sum(1 for u in usables if u))
    return {
        "n_trials": CTXMAX_N,
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
        "ctxplus_mean_leff": float(CTXPLUS_MEAN_LEFF),
        "min_usable": MIN_USABLE,
        "min_sources": MIN_SOURCES,
        "top_k": TOP_K_SLICES_MAX,
        "pass_usable": n_usable >= MIN_USABLE,
        "pass_multi_source": float(mean_sources) >= float(MIN_SOURCES)
        and int(n_multi_source) >= MIN_USABLE,
        "pass_leff_up": float(mean_l_eff) > float(CTXPLUS_MEAN_LEFF),
        "pass_active": float(mean_active) <= float(ACTIVE_CAP),
        "pass_slices": float(mean_slices) >= float(TOP_K_SLICES_MAX),
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "pack_ids": [p["id"] for p in AE0_PACK],
    }


def decide_ctxmax(stats: Mapping[str, Any]) -> str:
    """
    GIVEN CTXMAX stats
    WHEN applying pesquisa §5 AE1 gate
    THEN PROMOTE if usable≥7 ∧ L_eff↑ ∧ multi-doc ∧ quality ∧ no false-hit;
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
