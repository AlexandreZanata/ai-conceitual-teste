"""Contract: Wave AO2 H-CTXCORE — dodeca-doc dual-arm (pesquisa §3)."""

from __future__ import annotations

from ctxcore_ops import (
    CTXCORE_COMPANIONS,
    CTXCORE_ID,
    CTXCORE_N,
    CTXEDGE_MEAN_LEFF,
    MIN_GEN_USABLE,
    MIN_LOOKUP_USABLE,
    MIN_SOURCES,
    TOP_K_SLICES_CORE,
    companions_for,
    ctxcore_doc_meta,
    ctxcore_stats,
    decide_ctxcore,
    score_ctxcore_gen,
    score_ctxcore_lookup,
)
from ctxedge_ops import TOP_K_SLICES_EDGE


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AO2 H-CTXCORE
    assert CTXCORE_ID == "H-CTXCORE"
    assert CTXCORE_N == 10
    assert MIN_LOOKUP_USABLE == 7
    assert MIN_GEN_USABLE == 5
    assert MIN_SOURCES == 12
    assert TOP_K_SLICES_CORE == 25
    assert TOP_K_SLICES_CORE > TOP_K_SLICES_EDGE
    assert CTXEDGE_MEAN_LEFF == 242448.4


def test_given_ao0_sources_when_pair_then_all_mapped_distinct() -> None:
    from ao_session_ops import AO0_PACK

    for item in AO0_PACK:
        primary = item["source_id"]
        comps = companions_for(primary)
        assert len(comps) == 11
        assert len({primary, *comps}) == 12
        assert CTXCORE_COMPANIONS[primary] == comps


def test_given_dodeca_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    docs = [list(range(i * 6000, i * 6000 + 5000)) for i in range(12)]
    q = [10, 20, 400, 800]
    sources = [f"s{i}" for i in range(12)]
    meta = ctxcore_doc_meta(docs, q, source_ids=sources)
    assert meta["n_sources"] == 12
    assert meta["k_slices"] == 25
    assert meta["deeper_than_ctxedge_k"] is True
    assert meta["l_eff"] >= 0
    assert meta["multi_source"] is True


def test_given_lookup_true_hit_when_score_then_usable() -> None:
    meta = {
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "n_sources": 12,
        "n_slices": 60,
        "l_eff": 300000,
        "k_slices": 25,
    }
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, usable = score_ctxcore_lookup(
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
        "n_sources": 12,
        "n_slices": 60,
        "l_eff": 300000,
        "k_slices": 25,
    }
    payload = {"mode": "DECODE", "wall_ms": 40.0, "n_new": 16}
    _score, _err, notes, usable = score_ctxcore_gen(
        completion="........",
        expected_gold="anything",
        meta=meta,
        payload=payload,
    )
    assert usable is True
    assert any("long-ctx" in n for n in notes)


def test_given_ready_stats_when_decide_then_promote() -> None:
    stats = ctxcore_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=300000.0,
        mean_active=352.0,
        mean_slices=250.0,
        mean_sources=12.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxcore(stats) == "PROMOTE"


def test_given_low_leff_when_decide_then_hold() -> None:
    stats = ctxcore_stats(
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
        mean_slices=250.0,
        mean_sources=12.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxcore(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxcore_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        mean_l_eff=300000.0,
        mean_active=352.0,
        mean_slices=250.0,
        mean_sources=12.0,
        n_fix=0,
    )
    assert decide_ctxcore(stats) == "KILL"
