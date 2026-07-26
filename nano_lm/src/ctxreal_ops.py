"""Wave AG2 H-CTXREAL: quad-doc beyond CTXULTRA; dual-arm Cursor EVAL."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from antifp_ops import (
    classify_arm,
    extract_telemetry,
    score_antifp_completion,
)
from ctxplus_ops import (
    ACTIVE_CAP,
    MIN_LEFF,
    MIN_LEFF_RATIO,
    ctxplus_doc_meta,
)
from ctxultra_ops import TOP_K_SLICES_ULTRA
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "CTXREAL_ID",
    "CTXREAL_N",
    "MIN_LOOKUP_USABLE",
    "MIN_GEN_USABLE",
    "MIN_SOURCES",
    "TOP_K_SLICES_REAL",
    "CTXULTRA_MEAN_LEFF",
    "CTXREAL_SECONDARY",
    "CTXREAL_TERTIARY",
    "CTXREAL_QUATERNARY",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "ACTIVE_CAP",
    "secondary_for",
    "tertiary_for",
    "quaternary_for",
    "ctxreal_doc_meta",
    "score_ctxreal_lookup",
    "score_ctxreal_gen",
    "ctxreal_stats",
    "decide_ctxreal",
]

CTXREAL_ID = "H-CTXREAL"
CTXREAL_N = 10
MIN_LOOKUP_USABLE = 7
MIN_GEN_USABLE = 5  # pesquisa §5 AG2 — gen-arm usable ≥5/10 long
MIN_SOURCES = 4
# Deeper than CTXULTRA K=7.
TOP_K_SLICES_REAL = 9
# Evidence: docs/results/nano-lm/formal-hctxultra-ctxultra.md
CTXULTRA_MEAN_LEFF = 56965.0

# Primary AG0 source_id → secondary / tertiary / quaternary.
CTXREAL_SECONDARY: Mapping[str, str] = {
    "bip-0032": "bip-0039",
    "bip-0039": "bip-0032",
    "bip-0340": "bip-0141",
    "python-tutorial-datastructures": "python-tutorial-classes",
    "python-tutorial-io": "python-tutorial-datastructures",
    "rust-book-ch03": "rust-book-ch03-02",
    "bitcoin-json-rpc": "bitcoin-rest",
    "bitcoin-rest": "bitcoin-json-rpc",
    "bip-0141": "bip-0340",
    "rfc8949": "rfc8446",
}

CTXREAL_TERTIARY: Mapping[str, str] = {
    "bip-0032": "bip-0141",
    "bip-0039": "bip-0340",
    "bip-0340": "bip-0032",
    "python-tutorial-datastructures": "python-tutorial-io",
    "python-tutorial-io": "python-tutorial-classes",
    "rust-book-ch03": "rust-book-ch04-01",
    "bitcoin-json-rpc": "bitcoin-core-readme",
    "bitcoin-rest": "bitcoin-developer-notes",
    "bip-0141": "bitcoin-core-readme",
    "rfc8949": "rfc791",
}

CTXREAL_QUATERNARY: Mapping[str, str] = {
    "bip-0032": "rfc8949",
    "bip-0039": "rfc8949",
    "bip-0340": "rfc8949",
    "python-tutorial-datastructures": "python-tutorial-intro",
    "python-tutorial-io": "python-tutorial-control",
    "rust-book-ch03": "rfc8949",
    "bitcoin-json-rpc": "rfc8949",
    "bitcoin-rest": "rfc8949",
    "bip-0141": "rfc8949",
    "rfc8949": "python-tutorial-datastructures",
}


def secondary_for(source_id: str) -> str:
    sid = str(source_id)
    if sid not in CTXREAL_SECONDARY:
        raise KeyError(f"no CTXREAL secondary for {sid}")
    return str(CTXREAL_SECONDARY[sid])


def tertiary_for(source_id: str) -> str:
    sid = str(source_id)
    if sid not in CTXREAL_TERTIARY:
        raise KeyError(f"no CTXREAL tertiary for {sid}")
    return str(CTXREAL_TERTIARY[sid])


def quaternary_for(source_id: str) -> str:
    sid = str(source_id)
    if sid not in CTXREAL_QUATERNARY:
        raise KeyError(f"no CTXREAL quaternary for {sid}")
    return str(CTXREAL_QUATERNARY[sid])


def ctxreal_doc_meta(
    primary_ids: Sequence[int],
    secondary_ids: Sequence[int],
    tertiary_ids: Sequence[int],
    quaternary_ids: Sequence[int],
    question_ids: Sequence[int],
    *,
    primary_source: str,
    secondary_source: str,
    tertiary_source: str,
    quaternary_source: str,
    k: int = TOP_K_SLICES_REAL,
) -> dict[str, Any]:
    """
    GIVEN four curated docs + question tokens
    WHEN building CTXREAL context
    THEN quad multi-slice metas with n_sources≥4 and L_eff vs CTXULTRA.
    """
    docs = (
        ("primary", primary_ids, primary_source),
        ("secondary", secondary_ids, secondary_source),
        ("tertiary", tertiary_ids, tertiary_source),
        ("quaternary", quaternary_ids, quaternary_source),
    )
    parts: dict[str, Any] = {}
    combined_l = 0
    combined_slices = 0
    for key, ids, src in docs:
        meta = ctxplus_doc_meta(ids, question_ids, k=k)
        parts[key] = meta
        parts[f"{key}_source"] = str(src)
        parts[f"{key}_l_eff"] = int(meta["l_eff"])
        parts[f"{key}_slices"] = int(meta["n_slices"])
        combined_l += int(meta["l_eff"])
        combined_slices += int(meta["n_slices"])
    active = int(parts["primary"]["sumcache_active"])
    ratio_ok = bool(parts["primary"]["ratio_ok"]) or (
        float(combined_l) >= float(MIN_LEFF) * float(MIN_LEFF_RATIO)
    )
    return {
        **{k: parts[k] for k in ("primary", "secondary", "tertiary", "quaternary")},
        "primary_source": str(primary_source),
        "secondary_source": str(secondary_source),
        "tertiary_source": str(tertiary_source),
        "quaternary_source": str(quaternary_source),
        "n_sources": MIN_SOURCES,
        "k_slices": int(k),
        "l_eff": int(combined_l),
        "n_slices": int(combined_slices),
        "sumcache_active": int(active),
        "ctx_bounded": active <= int(ACTIVE_CAP),
        "l_eff_ok": int(combined_l) >= int(MIN_LEFF),
        "ratio_ok": bool(ratio_ok),
        "multi_source": True,
        "above_ctxultra_leff": float(combined_l) > float(CTXULTRA_MEAN_LEFF),
        "deeper_than_ctxultra_k": int(k) > int(TOP_K_SLICES_ULTRA),
    }


def _ctx_ok(meta: Mapping[str, Any]) -> bool:
    n_src = int(meta.get("n_sources") or 0)
    ok = bool(meta.get("l_eff_ok")) and bool(meta.get("ratio_ok"))
    ok = ok and bool(meta.get("ctx_bounded")) and n_src >= MIN_SOURCES
    return ok and int(meta.get("n_slices") or 0) >= 1


def score_ctxreal_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    meta: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN LOOKUP arm + quad-doc meta
    WHEN Cursor EVAL
    THEN score labeled LOOKUP (not gen IQ); usable if score≥8 ∧ ctx_ok.
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
        (
            f"CTXREAL quad L_eff={meta.get('l_eff')} "
            f"sources={meta.get('n_sources')} k={meta.get('k_slices')} "
            f"— LOOKUP product path ≠ generative IQ"
        ),
    ]
    ctx_ok = _ctx_ok(meta)
    if arm != "LOOKUP":
        return score, True, notes + ["LOOKUP arm mislabeled"], False
    usable = (not err) and score >= 8.0 and ctx_ok
    if not ctx_ok and not err:
        return score, True, notes + ["FIX: quad-doc/ctx gate failed"], False
    return float(score), bool(err), notes, bool(usable)


def score_ctxreal_gen(
    *,
    completion: str,
    expected_gold: str,
    meta: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """
    GIVEN GENERATE arm + quad-doc meta
    WHEN Cursor EVAL completion (not TRUE_HIT→9)
    THEN usable_long iff ctx_ok ∧ wall_ms>0 ∧ n_new>0 (long gen path).
    """
    score, err, notes = score_antifp_completion(
        arm="GENERATE",
        completion=completion,
        gold=expected_gold,
    )
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    ctx_ok = _ctx_ok(meta)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        (
            f"CTXREAL gen long-ctx L_eff={meta.get('l_eff')} "
            f"sources={meta.get('n_sources')} — scored completion, not LOOKUP"
        ),
    ]
    gen_ok = arm == "GENERATE" and tel["wall_ms"] > 0.0 and tel["n_new"] > 0
    usable = bool(ctx_ok and gen_ok)
    if not usable:
        err = True
        notes.append("FIX: gen long-ctx usable gate failed")
    return float(score), bool(err), notes, bool(usable)


def ctxreal_stats(
    *,
    lookup_scores: Sequence[float],
    lookup_errors: Sequence[bool],
    lookup_usables: Sequence[bool],
    gen_scores: Sequence[float],
    gen_errors: Sequence[bool],
    gen_usables: Sequence[bool],
    n_true_hit: int,
    n_false_hit: int,
    mean_l_eff: float,
    mean_active: float,
    mean_slices: float,
    mean_sources: float,
    n_fix: int,
) -> dict[str, Any]:
    """
    GIVEN dual-arm CTXREAL ×10
    WHEN summarizing AG2
    THEN L_eff↑ vs CTXULTRA · gen usable≥5 · lookup usable≥7.
    """
    if len(lookup_scores) != CTXREAL_N or len(gen_scores) != CTXREAL_N:
        raise ValueError(f"CTXREAL requires {CTXREAL_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(CTXREAL_N))
    g_mean = float(sum(gen_scores) / float(CTXREAL_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_l_u = int(sum(1 for u in lookup_usables if u))
    n_g_u = int(sum(1 for u in gen_usables if u))
    return {
        "n_trials": CTXREAL_N,
        "lookup_mean": l_mean,
        "gen_mean": g_mean,
        "n_lookup_errors": n_l_err,
        "n_gen_errors": n_g_err,
        "n_lookup_usable": n_l_u,
        "n_gen_usable": n_g_u,
        "n_true_hit": int(n_true_hit),
        "n_false_hit": int(n_false_hit),
        "mean_l_eff": float(mean_l_eff),
        "mean_active": float(mean_active),
        "mean_slices": float(mean_slices),
        "mean_sources": float(mean_sources),
        "n_fix": int(n_fix),
        "ctxultra_mean_leff": float(CTXULTRA_MEAN_LEFF),
        "min_lookup_usable": MIN_LOOKUP_USABLE,
        "min_gen_usable": MIN_GEN_USABLE,
        "min_sources": MIN_SOURCES,
        "top_k": TOP_K_SLICES_REAL,
        "pass_lookup_usable": n_l_u >= MIN_LOOKUP_USABLE,
        "pass_gen_usable": n_g_u >= MIN_GEN_USABLE,
        "pass_multi_source": float(mean_sources) >= float(MIN_SOURCES),
        "pass_leff_up": float(mean_l_eff) > float(CTXULTRA_MEAN_LEFF),
        "pass_active": float(mean_active) <= float(ACTIVE_CAP),
        "pass_slices": float(mean_slices) >= float(TOP_K_SLICES_REAL),
        "pass_lookup_quality": l_mean >= PASS_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_ctxreal(stats: Mapping[str, Any]) -> str:
    """
    GIVEN CTXREAL stats
    WHEN applying pesquisa §5 AG2 gate
    THEN PROMOTE if L_eff↑ ∧ quad-doc ∧ gen usable≥5 ∧ lookup ok ∧ no false-hit;
         HOLD if dual-arm ok but soft-fail; KILL if false-hit.
    """
    if int(stats.get("n_false_hit", 0)) > 0:
        return "KILL"
    ok = (
        bool(stats.get("pass_leff_up"))
        and bool(stats.get("pass_multi_source"))
        and bool(stats.get("pass_active"))
        and bool(stats.get("pass_slices"))
        and bool(stats.get("pass_lookup_usable"))
        and bool(stats.get("pass_gen_usable"))
        and bool(stats.get("pass_lookup_quality"))
        and bool(stats.get("dual_arm"))
    )
    if ok:
        return "PROMOTE"
    return "HOLD"
