"""Contract: Wave AJ2 H-CTXPEAK — hepta-doc dual-arm (pesquisa §3)."""

from __future__ import annotations

from ctxpeak_ops import (
    CTXPUSH_MEAN_LEFF,
    CTXPEAK_COMPANIONS,
    CTXPEAK_ID,
    CTXPEAK_N,
    MIN_GEN_USABLE,
    MIN_LOOKUP_USABLE,
    MIN_SOURCES,
    TOP_K_SLICES_PEAK,
    companions_for,
    ctxpeak_doc_meta,
    ctxpeak_stats,
    decide_ctxpeak,
    score_ctxpeak_gen,
    score_ctxpeak_lookup,
)
from ctxpush_ops import TOP_K_SLICES_PUSH


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AJ2 H-CTXPEAK
    assert CTXPEAK_ID == "H-CTXPEAK"
    assert CTXPEAK_N == 10
    assert MIN_LOOKUP_USABLE == 7
    assert MIN_GEN_USABLE == 5
    assert MIN_SOURCES == 7
    assert TOP_K_SLICES_PEAK == 15
    assert TOP_K_SLICES_PEAK > TOP_K_SLICES_PUSH
    assert CTXPUSH_MEAN_LEFF == 162851.0


def test_given_aj0_sources_when_pair_then_all_mapped_distinct() -> None:
    from aj_session_ops import AJ0_PACK

    for item in AJ0_PACK:
        primary = item["source_id"]
        comps = companions_for(primary)
        assert len(comps) == 6
        assert len({primary, *comps}) == 7
        assert CTXPEAK_COMPANIONS[primary] == comps


def test_given_hepta_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    docs = [list(range(i * 6000, i * 6000 + 5000)) for i in range(7)]
    q = [10, 20, 400, 800]
    sources = [f"s{i}" for i in range(7)]
    meta = ctxpeak_doc_meta(
        docs,
        q,
        source_ids=sources,
    )
    assert meta["n_sources"] == 7
    assert meta["k_slices"] == 15
    assert meta["deeper_than_ctxpush_k"] is True
    assert meta["l_eff"] >= 0
    assert meta["multi_source"] is True


def test_given_lookup_true_hit_when_score_then_usable() -> None:
    meta = {
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "n_sources": 7,
        "n_slices": 20,
        "l_eff": 200000,
        "k_slices": 15,
    }
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, usable = score_ctxpeak_lookup(
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
        "n_sources": 7,
        "n_slices": 20,
        "l_eff": 200000,
        "k_slices": 15,
    }
    payload = {"mode": "DECODE", "wall_ms": 40.0, "n_new": 16}
    _score, _err, notes, usable = score_ctxpeak_gen(
        completion="........",
        expected_gold="anything",
        meta=meta,
        payload=payload,
    )
    assert usable is True
    assert any("long-ctx" in n for n in notes)


def test_given_ready_stats_when_decide_then_promote() -> None:
    stats = ctxpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=200000.0,
        mean_active=352.0,
        mean_slices=105.0,
        mean_sources=7.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxpeak(stats) == "PROMOTE"


def test_given_low_leff_when_decide_then_hold() -> None:
    stats = ctxpeak_stats(
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
        mean_slices=105.0,
        mean_sources=7.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxpeak(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        mean_l_eff=200000.0,
        mean_active=352.0,
        mean_slices=105.0,
        mean_sources=7.0,
        n_fix=0,
    )
    assert decide_ctxpeak(stats) == "KILL"
