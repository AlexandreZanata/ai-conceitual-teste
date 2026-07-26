"""Contract: Wave AG2 H-CTXREAL — quad-doc dual-arm (pesquisa §5)."""

from __future__ import annotations

from ctxreal_ops import (
    CTXREAL_ID,
    CTXREAL_N,
    CTXREAL_QUATERNARY,
    CTXREAL_SECONDARY,
    CTXREAL_TERTIARY,
    CTXULTRA_MEAN_LEFF,
    MIN_GEN_USABLE,
    MIN_LOOKUP_USABLE,
    MIN_SOURCES,
    TOP_K_SLICES_REAL,
    ctxreal_doc_meta,
    ctxreal_stats,
    decide_ctxreal,
    quaternary_for,
    score_ctxreal_gen,
    score_ctxreal_lookup,
    secondary_for,
    tertiary_for,
)
from ctxultra_ops import TOP_K_SLICES_ULTRA


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AG2 H-CTXREAL
    assert CTXREAL_ID == "H-CTXREAL"
    assert CTXREAL_N == 10
    assert MIN_LOOKUP_USABLE == 7
    assert MIN_GEN_USABLE == 5
    assert MIN_SOURCES == 4
    assert TOP_K_SLICES_REAL == 9
    assert TOP_K_SLICES_REAL > TOP_K_SLICES_ULTRA
    assert CTXULTRA_MEAN_LEFF == 56965.0


def test_given_ag0_sources_when_pair_then_all_mapped_distinct() -> None:
    from ag_session_ops import AG0_PACK

    for item in AG0_PACK:
        primary = item["source_id"]
        sec = secondary_for(primary)
        ter = tertiary_for(primary)
        quat = quaternary_for(primary)
        assert len({primary, sec, ter, quat}) == 4
        assert CTXREAL_SECONDARY[primary] == sec
        assert CTXREAL_TERTIARY[primary] == ter
        assert CTXREAL_QUATERNARY[primary] == quat


def test_given_quad_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    primary = list(range(1500))
    secondary = list(range(2000, 3500))
    tertiary = list(range(4000, 5500))
    quaternary = list(range(6000, 7500))
    q = [10, 20, 400, 800]
    meta = ctxreal_doc_meta(
        primary,
        secondary,
        tertiary,
        quaternary,
        q,
        primary_source="a",
        secondary_source="b",
        tertiary_source="c",
        quaternary_source="d",
    )
    assert meta["n_sources"] == 4
    assert meta["multi_source"] is True
    assert meta["k_slices"] == TOP_K_SLICES_REAL
    assert meta["n_slices"] == TOP_K_SLICES_REAL * 4
    assert meta["l_eff"] == 1500 * 4
    assert meta["deeper_than_ctxultra_k"] is True
    assert meta["above_ctxultra_leff"] is False  # 6000 < 56965


def test_given_lookup_true_hit_when_score_then_usable() -> None:
    meta = {
        "n_sources": 4,
        "l_eff": 90000,
        "sumcache_active": 352,
        "n_slices": 36,
        "k_slices": 9,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
    }
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, usable = score_ctxreal_lookup(
        mode="WRAP_LOOKUP",
        completion="gold answer",
        expected_gold="gold answer",
        lookup_kind="TRUE_HIT",
        meta=meta,
        payload=payload,
    )
    assert score >= 8.0 and err is False and usable is True
    assert any("≠ generative IQ" in n or "not generative" in n for n in notes)


def test_given_gen_periods_when_score_then_usable_if_ctx_ok() -> None:
    meta = {
        "n_sources": 4,
        "l_eff": 90000,
        "sumcache_active": 352,
        "n_slices": 36,
        "k_slices": 9,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
    }
    payload = {"mode": "QT+EARLY n=1", "wall_ms": 20.0, "n_new": 8}
    score, err, notes, usable = score_ctxreal_gen(
        completion="........",
        expected_gold="anything",
        meta=meta,
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert usable is True  # long-ctx gen path ready despite period collapse
    assert notes


def test_given_gen_zero_wall_when_score_then_not_usable() -> None:
    meta = {
        "n_sources": 4,
        "l_eff": 90000,
        "sumcache_active": 352,
        "n_slices": 36,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
    }
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    _s, _e, _n, usable = score_ctxreal_gen(
        completion="x",
        expected_gold="y",
        meta=meta,
        payload=payload,
    )
    assert usable is False


def test_given_ready_when_decide_then_promote() -> None:
    stats = ctxreal_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=90000.0,
        mean_active=300.0,
        mean_slices=36.0,
        mean_sources=4.0,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert stats["pass_gen_usable"] is True
    assert decide_ctxreal(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxreal_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=[True] * 10,
        n_true_hit=9,
        n_false_hit=1,
        mean_l_eff=90000.0,
        mean_active=300.0,
        mean_slices=36.0,
        mean_sources=4.0,
        n_fix=0,
    )
    assert decide_ctxreal(stats) == "KILL"


def test_given_low_gen_usable_when_decide_then_hold() -> None:
    usables = [True] * 4 + [False] * 6
    stats = ctxreal_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        lookup_usables=[True] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        gen_usables=usables,
        n_true_hit=10,
        n_false_hit=0,
        mean_l_eff=90000.0,
        mean_active=300.0,
        mean_slices=36.0,
        mean_sources=4.0,
        n_fix=0,
    )
    assert decide_ctxreal(stats) == "HOLD"
