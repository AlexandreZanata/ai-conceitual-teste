"""Wave AD2 H-COMPOSE: multi-source CTXPLUS compose on held-out asks."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from ad_session_ops import AD0_PACK
from ctxplus_ops import (
    ACTIVE_CAP,
    MIN_LEFF,
    MIN_LEFF_RATIO,
    ctxplus_doc_meta,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "COMPOSE_ID",
    "COMPOSE_N",
    "MIN_USABLE",
    "MIN_SOURCES",
    "COMPOSE_SECONDARY",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "secondary_for",
    "compose_doc_meta",
    "score_compose_trial",
    "compose_stats",
    "decide_compose",
]

COMPOSE_ID = "H-COMPOSE"
COMPOSE_N = 10
MIN_USABLE = 7  # §13.1 AD2
MIN_SOURCES = 2

# Primary AD0 source_id → secondary curated source for multi-source compose.
COMPOSE_SECONDARY: Mapping[str, str] = {
    "bip-0340": "bip-0141",
    "bip-0141": "bip-0340",
    "python-tutorial-datastructures": "python-tutorial-control",
    "python-tutorial-io": "python-tutorial-intro",
    "rust-book-ch04-01": "rust-book-ch03",
    "rust-book-ch05-01": "rust-book-ch04-01",
    "bitcoin-developer-notes": "bitcoin-core-readme",
    "rfc8949": "rfc791",
    "rfc791": "rfc8949",
    "bitcoin-core-readme": "bitcoin-developer-notes",
}


def secondary_for(source_id: str) -> str:
    """
    GIVEN primary source_id
    WHEN resolving COMPOSE pair
    THEN return secondary curated id (raises if unknown).
    """
    sid = str(source_id)
    if sid not in COMPOSE_SECONDARY:
        raise KeyError(f"no COMPOSE secondary for {sid}")
    return str(COMPOSE_SECONDARY[sid])


def compose_doc_meta(
    primary_ids: Sequence[int],
    secondary_ids: Sequence[int],
    question_ids: Sequence[int],
    *,
    primary_source: str,
    secondary_source: str,
) -> dict[str, Any]:
    """
    GIVEN two curated doc token streams + question tokens
    WHEN building COMPOSE context
    THEN dual CTXPLUS metas with n_sources≥2 and combined L_eff/slices.
    """
    primary = ctxplus_doc_meta(primary_ids, question_ids)
    secondary = ctxplus_doc_meta(secondary_ids, question_ids)
    combined_l = int(primary["l_eff"]) + int(secondary["l_eff"])
    combined_slices = int(primary["n_slices"]) + int(secondary["n_slices"])
    combined_union = int(primary["slice_union"]) + int(secondary["slice_union"])
    # Bound active to primary SUMCACHE cap (serve window still ≤ ACTIVE_CAP).
    active = int(primary["sumcache_active"])
    ratio_ok = bool(primary["ratio_ok"]) or (
        float(combined_l) >= float(MIN_LEFF) * float(MIN_LEFF_RATIO)
    )
    return {
        "primary_source": str(primary_source),
        "secondary_source": str(secondary_source),
        "n_sources": MIN_SOURCES,
        "l_eff": int(combined_l),
        "primary_l_eff": int(primary["l_eff"]),
        "secondary_l_eff": int(secondary["l_eff"]),
        "n_slices": int(combined_slices),
        "primary_slices": int(primary["n_slices"]),
        "secondary_slices": int(secondary["n_slices"]),
        "slice_union": int(combined_union),
        "sumcache_active": int(active),
        "ctx_bounded": active <= int(ACTIVE_CAP),
        "l_eff_ok": int(combined_l) >= int(MIN_LEFF),
        "ratio_vs_roll_w": float(primary["ratio_vs_roll_w"]),
        "ratio_ok": bool(ratio_ok),
        "multi_source": True,
        "multi_deeper": bool(primary.get("multi_deeper"))
        or bool(secondary.get("multi_deeper")),
        "primary": primary,
        "secondary": secondary,
    }


def _ratio_ok(meta: Mapping[str, Any]) -> bool:
    return bool(meta.get("ratio_ok"))


def score_compose_trial(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    meta: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN COMPOSE ask + dual-source ctx meta
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
    ctx_ok = bool(meta.get("l_eff_ok")) and _ratio_ok(meta)
    ctx_ok = ctx_ok and bool(meta.get("ctx_bounded"))
    ctx_ok = ctx_ok and n_src >= MIN_SOURCES
    slices_ok = int(meta.get("n_slices") or 0) >= 1
    usable = (not err) and score >= 8.0 and ctx_ok and slices_ok
    notes = list(notes) + [
        (
            f"sources={n_src} L_eff={meta.get('l_eff')} "
            f"slices={meta.get('n_slices')} "
            f"active={meta.get('sumcache_active')} "
            f"pair={meta.get('primary_source')}+{meta.get('secondary_source')}"
        ),
        (
            "COMPOSE multi-source CTXPLUS — not STREAM / naive CTX"
            if ctx_ok and slices_ok
            else "FIX: multi-source/ctx gate failed"
        ),
    ]
    if (not ctx_ok or not slices_ok) and not err:
        return score, True, notes, False
    return score, err, notes, usable


def compose_stats(
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
    GIVEN 10 COMPOSE scores + ctx means
    WHEN summarizing AD2
    THEN quality + usable≥7 + multi-source.
    """
    if len(scores) != COMPOSE_N or len(errors) != COMPOSE_N:
        raise ValueError(f"COMPOSE requires exactly {COMPOSE_N} scores/errors")
    if len(usables) != COMPOSE_N:
        raise ValueError(f"COMPOSE requires exactly {COMPOSE_N} usable flags")
    mean = float(sum(scores) / float(COMPOSE_N))
    n_err = int(sum(1 for e in errors if e))
    n_usable = int(sum(1 for u in usables if u))
    return {
        "n_trials": COMPOSE_N,
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
        "min_usable": MIN_USABLE,
        "min_sources": MIN_SOURCES,
        "pass_usable": n_usable >= MIN_USABLE,
        "pass_multi_source": float(mean_sources) >= float(MIN_SOURCES)
        and int(n_multi_source) >= MIN_USABLE,
        "pass_active": float(mean_active) <= float(ACTIVE_CAP),
        "pass_slices": float(mean_slices) >= 1.0,
        "pass_quality": mean >= PASS_MEAN and n_err <= PASS_MAX_ERRORS,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
        "pack_ids": [p["id"] for p in AD0_PACK],
    }


def decide_compose(stats: Mapping[str, Any]) -> str:
    """
    GIVEN COMPOSE stats
    WHEN applying §8.6 / §13.1 AD2 gate
    THEN PROMOTE if usable≥7 ∧ multi-source ∧ quality ∧ no false-hit;
         HOLD if no false-hit but soft-fail; KILL if false-hit.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    ok = (
        bool(stats.get("pass_usable"))
        and bool(stats.get("pass_multi_source"))
        and bool(stats.get("pass_active"))
        and bool(stats.get("pass_slices"))
        and bool(stats.get("pass_quality"))
    )
    if ok:
        return "PROMOTE"
    return "HOLD"
