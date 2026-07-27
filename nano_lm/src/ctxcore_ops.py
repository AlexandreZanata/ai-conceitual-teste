"""Wave AO2 H-CTXCORE: dodeca-doc beyond CTXEDGE; dual-arm Cursor EVAL."""

from __future__ import annotations

from typing import Any, Mapping, Sequence

from antifp_ops import classify_arm, extract_telemetry
from asksmart_ops import strip_stop
from ctxedge_ops import TOP_K_SLICES_EDGE
from ctxplus_ops import (
    ACTIVE_CAP,
    MIN_LEFF,
    MIN_LEFF_RATIO,
    ctxplus_doc_meta,
)
from z_error_bank import PASS_MAX_ERRORS, PASS_MEAN

__all__ = [
    "CTXCORE_ID",
    "CTXCORE_N",
    "MIN_LOOKUP_USABLE",
    "MIN_GEN_USABLE",
    "MIN_SOURCES",
    "TOP_K_SLICES_CORE",
    "CTXEDGE_MEAN_LEFF",
    "CTXCORE_COMPANIONS",
    "PASS_MEAN",
    "PASS_MAX_ERRORS",
    "ACTIVE_CAP",
    "companions_for",
    "ctxcore_doc_meta",
    "score_ctxcore_lookup",
    "score_ctxcore_gen",
    "ctxcore_stats",
    "decide_ctxcore",
]

CTXCORE_ID = "H-CTXCORE"
CTXCORE_N = 10
MIN_LOOKUP_USABLE = 7
MIN_GEN_USABLE = 5
MIN_SOURCES = 12  # dodeca-doc beyond CTXEDGE undeca
# Deeper than CTXEDGE K=23.
TOP_K_SLICES_CORE = 25
# Evidence: docs/results/nano-lm/formal-hctxedge-ctxedge.md
CTXEDGE_MEAN_LEFF = 242448.4

# Primary AO0 source_id → eleven companions (all twelve incl. primary distinct).
CTXCORE_COMPANIONS: Mapping[
    str,
    tuple[str, str, str, str, str, str, str, str, str, str, str],
] = {
    "bip-0039": (
        "bip-0032",
        "bip-0141",
        "bip-0340",
        "rfc8446",
        "rfc8949",
        "bip-0001",
        "bitcoin-doc-bips",
        "bitcoin-rest",
        "bitcoin-json-rpc",
        "bitcoin-core-readme",
        "rust-book-ch03",
    ),
    "bip-0032": (
        "bip-0039",
        "bip-0141",
        "bip-0340",
        "rfc8446",
        "rfc8949",
        "bip-0001",
        "bitcoin-json-rpc",
        "bitcoin-core-readme",
        "bitcoin-developer-notes",
        "bitcoin-rest",
        "rust-book-ch03",
    ),
    "bip-0141": (
        "bip-0039",
        "bip-0032",
        "bip-0340",
        "rfc8446",
        "rfc8949",
        "bitcoin-doc-bips",
        "bip-0001",
        "bitcoin-developer-notes",
        "bitcoin-rest",
        "bitcoin-core-readme",
        "rust-book-ch03",
    ),
    "python-tutorial-datastructures": (
        "python-tutorial-classes",
        "python-tutorial-control",
        "python-tutorial-intro",
        "python-tutorial-io",
        "rfc791",
        "rust-book-ch03-02",
        "rust-book-ch04-01",
        "rust-book-ch05-01",
        "rust-book-ch03",
        "rfc8446",
        "bitcoin-developer-notes",
    ),
    "python-tutorial-control": (
        "python-tutorial-classes",
        "python-tutorial-datastructures",
        "python-tutorial-intro",
        "python-tutorial-io",
        "rfc791",
        "rust-book-ch03",
        "rust-book-ch05-01",
        "rust-book-ch04-01",
        "rust-book-ch03-02",
        "rfc8949",
        "bitcoin-developer-notes",
    ),
    "python-tutorial-classes": (
        "python-tutorial-datastructures",
        "python-tutorial-control",
        "python-tutorial-intro",
        "python-tutorial-io",
        "rfc791",
        "rust-book-ch05-01",
        "rust-book-ch03-02",
        "rust-book-ch03",
        "rust-book-ch04-01",
        "rfc8446",
        "bitcoin-developer-notes",
    ),
    "rust-book-ch03-02": (
        "rust-book-ch03",
        "rust-book-ch04-01",
        "rust-book-ch05-01",
        "rfc8949",
        "rfc8446",
        "python-tutorial-intro",
        "python-tutorial-control",
        "python-tutorial-datastructures",
        "python-tutorial-classes",
        "python-tutorial-io",
        "bitcoin-developer-notes",
    ),
    "rust-book-ch05-01": (
        "rust-book-ch03-02",
        "rust-book-ch03",
        "rust-book-ch04-01",
        "rfc8949",
        "rfc8446",
        "python-tutorial-classes",
        "python-tutorial-intro",
        "python-tutorial-io",
        "python-tutorial-datastructures",
        "python-tutorial-control",
        "bitcoin-developer-notes",
    ),
    "bitcoin-rest": (
        "bitcoin-json-rpc",
        "bitcoin-core-readme",
        "bitcoin-developer-notes",
        "bip-0032",
        "rfc8446",
        "rfc8949",
        "bip-0001",
        "bip-0141",
        "bitcoin-doc-bips",
        "bip-0039",
        "rust-book-ch03",
    ),
    "rfc791": (
        "rfc8446",
        "rfc8949",
        "bip-0039",
        "python-tutorial-intro",
        "bitcoin-json-rpc",
        "bip-0001",
        "bitcoin-rest",
        "bitcoin-doc-bips",
        "bip-0032",
        "python-tutorial-io",
        "rust-book-ch03",
    ),
}

_DOC_KEYS = (
    "primary",
    "secondary",
    "tertiary",
    "quaternary",
    "quinary",
    "senary",
    "septenary",
    "octonary",
    "nonary",
    "denary",
    "undenary",
    "duodenary",
)


def companions_for(
    source_id: str,
) -> tuple[str, str, str, str, str, str, str, str, str, str, str]:
    """
    GIVEN AO0 primary source_id
    WHEN resolving CTXCORE companions
    THEN return eleven distinct companion ids.
    """
    sid = str(source_id)
    if sid not in CTXCORE_COMPANIONS:
        raise KeyError(f"no CTXCORE companions for {sid}")
    return CTXCORE_COMPANIONS[sid]


def ctxcore_doc_meta(
    doc_token_ids: Sequence[Sequence[int]],
    question_ids: Sequence[int],
    *,
    source_ids: Sequence[str],
    k: int = TOP_K_SLICES_CORE,
) -> dict[str, Any]:
    """
    GIVEN twelve curated docs + question tokens
    WHEN building CTXCORE context
    THEN dodeca multi-slice metas with n_sources≥12 and L_eff vs CTXEDGE.
    """
    if len(doc_token_ids) != MIN_SOURCES or len(source_ids) != MIN_SOURCES:
        raise ValueError(f"CTXCORE requires {MIN_SOURCES} docs/sources")
    if len(set(source_ids)) != MIN_SOURCES:
        raise ValueError("CTXCORE sources must be distinct")
    parts: dict[str, Any] = {}
    combined_l = 0
    combined_slices = 0
    for key, ids, src in zip(_DOC_KEYS, doc_token_ids, source_ids, strict=True):
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
        **{k: parts[k] for k in _DOC_KEYS},
        **{f"{k}_source": parts[f"{k}_source"] for k in _DOC_KEYS},
        "n_sources": MIN_SOURCES,
        "k_slices": int(k),
        "l_eff": int(combined_l),
        "n_slices": int(combined_slices),
        "sumcache_active": int(active),
        "ctx_bounded": active <= int(ACTIVE_CAP),
        "l_eff_ok": int(combined_l) >= int(MIN_LEFF),
        "ratio_ok": bool(ratio_ok),
        "multi_source": True,
        "above_ctxedge_leff": float(combined_l) > float(CTXEDGE_MEAN_LEFF),
        "deeper_than_ctxedge_k": int(k) > int(TOP_K_SLICES_EDGE),
    }


def _ctx_ok(meta: Mapping[str, Any]) -> bool:
    n_src = int(meta.get("n_sources") or 0)
    ok = bool(meta.get("l_eff_ok")) and bool(meta.get("ratio_ok"))
    ok = ok and bool(meta.get("ctx_bounded")) and n_src >= MIN_SOURCES
    return ok and int(meta.get("n_slices") or 0) >= 1


def score_ctxcore_lookup(
    *,
    mode: str,
    completion: str,
    expected_gold: str,
    lookup_kind: str,
    meta: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """LOOKUP arm + dodeca-doc — labeled LOOKUP ≠ gen IQ."""
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
            f"CTXCORE dodeca L_eff={meta.get('l_eff')} "
            f"sources={meta.get('n_sources')} k={meta.get('k_slices')} "
            f"— LOOKUP product path ≠ generative IQ"
        ),
    ]
    ctx_ok = _ctx_ok(meta)
    if arm != "LOOKUP":
        return score, True, notes + ["LOOKUP arm mislabeled"], False
    usable = (not err) and score >= 8.0 and ctx_ok
    if not ctx_ok and not err:
        return score, True, notes + ["FIX: dodeca-doc/ctx gate failed"], False
    return float(score), bool(err), notes, bool(usable)


def score_ctxcore_gen(
    *,
    completion: str,
    expected_gold: str,
    meta: Mapping[str, Any],
    payload: Mapping[str, Any],
) -> tuple[float, bool, list[str], bool]:
    """GENERATE arm — usable_long iff ctx_ok ∧ wall_ms>0 ∧ n_new>0."""
    from servealign_ops import score_open_completion

    text = strip_stop(completion)
    score, err, notes = score_open_completion(text, expected_gold)
    tel = extract_telemetry(payload)
    arm = classify_arm(payload)
    ctx_ok = _ctx_ok(meta)
    notes = list(notes) + [
        f"arm={arm} mode={tel['mode']} wall_ms={tel['wall_ms']} "
        f"n_new={tel['n_new']}",
        (
            f"CTXCORE gen long-ctx L_eff={meta.get('l_eff')} "
            f"sources={meta.get('n_sources')} — scored completion, not LOOKUP"
        ),
    ]
    gen_ok = arm == "GENERATE" and tel["wall_ms"] > 0.0 and tel["n_new"] > 0
    usable = bool(ctx_ok and gen_ok)
    if not usable:
        err = True
        notes.append("FIX: gen long-ctx usable gate failed")
    return float(score), bool(err), notes, bool(usable)


def ctxcore_stats(
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
    """Summarize AO2: L_eff↑ vs CTXEDGE · dodeca · gen usable≥5."""
    if len(lookup_scores) != CTXCORE_N or len(gen_scores) != CTXCORE_N:
        raise ValueError(f"CTXCORE requires {CTXCORE_N} dual-arm scores")
    l_mean = float(sum(lookup_scores) / float(CTXCORE_N))
    g_mean = float(sum(gen_scores) / float(CTXCORE_N))
    n_l_err = int(sum(1 for e in lookup_errors if e))
    n_g_err = int(sum(1 for e in gen_errors if e))
    n_l_u = int(sum(1 for u in lookup_usables if u))
    n_g_u = int(sum(1 for u in gen_usables if u))
    return {
        "n_trials": CTXCORE_N,
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
        "ctxedge_mean_leff": float(CTXEDGE_MEAN_LEFF),
        "min_lookup_usable": MIN_LOOKUP_USABLE,
        "min_gen_usable": MIN_GEN_USABLE,
        "min_sources": MIN_SOURCES,
        "top_k": TOP_K_SLICES_CORE,
        "pass_lookup_usable": n_l_u >= MIN_LOOKUP_USABLE,
        "pass_gen_usable": n_g_u >= MIN_GEN_USABLE,
        "pass_multi_source": float(mean_sources) >= float(MIN_SOURCES),
        "pass_leff_up": float(mean_l_eff) > float(CTXEDGE_MEAN_LEFF),
        "pass_active": float(mean_active) <= float(ACTIVE_CAP),
        "pass_slices": float(mean_slices) >= float(TOP_K_SLICES_CORE),
        "pass_lookup_quality": l_mean >= PASS_MEAN
        and n_l_err <= PASS_MAX_ERRORS,
        "dual_arm": True,
        "pass_mean": PASS_MEAN,
        "pass_max_errors": PASS_MAX_ERRORS,
    }


def decide_ctxcore(stats: Mapping[str, Any]) -> str:
    """
    GIVEN CTXCORE stats
    WHEN applying pesquisa §3 AO2 gate
    THEN PROMOTE if L_eff↑ vs CTXEDGE ∧ dodeca ∧ gen usable≥5 ∧ lookup ok;
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
