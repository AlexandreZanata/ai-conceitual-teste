"""Contract: Wave AM2 H-CTXNEXT — deca-doc dual-arm (pesquisa §3)."""

from __future__ import annotations

from ctxfresh_ops import TOP_K_SLICES_FRESH
from ctxnext_ops import (
    CTXFRESH_MEAN_LEFF,
    CTXNEXT_COMPANIONS,
    CTXNEXT_ID,
    CTXNEXT_N,
    MIN_GEN_USABLE,
    MIN_LOOKUP_USABLE,
    MIN_SOURCES,
    TOP_K_SLICES_NEXT,
    companions_for,
    ctxnext_doc_meta,
    ctxnext_stats,
    decide_ctxnext,
    score_ctxnext_gen,
    score_ctxnext_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AM2 H-CTXNEXT
    assert CTXNEXT_ID == "H-CTXNEXT"
    assert CTXNEXT_N == 10
    assert MIN_LOOKUP_USABLE == 7
    assert MIN_GEN_USABLE == 5
    assert MIN_SOURCES == 10
    assert TOP_K_SLICES_NEXT == 21
    assert TOP_K_SLICES_NEXT > TOP_K_SLICES_FRESH
    assert CTXFRESH_MEAN_LEFF == 200344.0


def test_given_am0_sources_when_pair_then_all_mapped_distinct() -> None:
    from am_session_ops import AM0_PACK

    for item in AM0_PACK:
        primary = item["source_id"]
        comps = companions_for(primary)
        assert len(comps) == 9
        assert len({primary, *comps}) == 10
        assert CTXNEXT_COMPANIONS[primary] == comps


def test_given_deca_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    docs = [list(range(i * 6000, i * 6000 + 5000)) for i in range(10)]
    q = [10, 20, 400, 800]
    sources = [f"s{i}" for i in range(10)]
    meta = ctxnext_doc_meta(docs, q, source_ids=sources)
    assert meta["n_sources"] == 10
    assert meta["k_slices"] == 21
    assert meta["deeper_than_ctxfresh_k"] is True
    assert meta["l_eff"] >= 0
    assert meta["multi_source"] is True


def test_given_lookup_true_hit_when_score_then_usable() -> None:
    meta = {
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "n_sources": 10,
        "n_slices": 40,
        "l_eff": 260000,
        "k_slices": 21,
    }
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, usable = score_ctxnext_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        meta=meta,
        payload=payload,
    )
    assert score >= 8.0 and err is False and usable is True
    assert any("LOOKUP product path" in n for n in notes)


def test_given_gen_telemetry_when_ctx_ok_then_usable() -> None:
    meta = {
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "n_sources": 10,
        "n_slices": 40,
        "l_eff": 260000,
        "k_slices": 21,
    }
    payload = {"mode": "DECODE", "wall_ms": 40.0, "n_new": 16}
    _score, _err, notes, usable = score_ctxnext_gen(
        completion="........",
        expected_gold="anything",
        meta=meta,
        payload=payload,
    )
    assert usable is True
    assert any("long-ctx" in n for n in notes)


def test_given_ready_stats_when_decide_then_promote() -> None:
    stats = ctxnext_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=260000.0,
        mean_active=352.0,
        mean_slices=180.0,
        mean_sources=10.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxnext(stats) == "PROMOTE"


def test_given_low_leff_when_decide_then_hold() -> None:
    stats = ctxnext_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=100000.0,
        mean_active=352.0,
        mean_slices=180.0,
        mean_sources=10.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxnext(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxnext_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        mean_l_eff=260000.0,
        mean_active=352.0,
        mean_slices=180.0,
        mean_sources=10.0,
        n_fix=0,
    )
    assert decide_ctxnext(stats) == "KILL"
