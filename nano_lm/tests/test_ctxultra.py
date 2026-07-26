"""Contract: Wave AF1 H-CTXULTRA — triple-doc; L_eff↑ vs CTXMAX."""

from __future__ import annotations

from ctxmax_ops import TOP_K_SLICES_MAX
from ctxultra_ops import (
    ACTIVE_CAP,
    CTXMAX_MEAN_LEFF,
    CTXULTRA_ID,
    CTXULTRA_N,
    CTXULTRA_SECONDARY,
    CTXULTRA_TERTIARY,
    MIN_SOURCES,
    MIN_USABLE,
    TOP_K_SLICES_ULTRA,
    ctxultra_doc_meta,
    ctxultra_stats,
    decide_ctxultra,
    score_ctxultra_trial,
    secondary_for,
    tertiary_for,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF1 H-CTXULTRA
    assert CTXULTRA_ID == "H-CTXULTRA"
    assert CTXULTRA_N == 10
    assert MIN_USABLE == 7
    assert MIN_SOURCES == 3
    assert TOP_K_SLICES_ULTRA == 7
    assert TOP_K_SLICES_ULTRA > TOP_K_SLICES_MAX
    assert CTXMAX_MEAN_LEFF == 31043.2


def test_given_af0_sources_when_pair_then_all_mapped_distinct() -> None:
    from af_session_ops import AF0_PACK

    for item in AF0_PACK:
        primary = item["source_id"]
        sec = secondary_for(primary)
        ter = tertiary_for(primary)
        assert sec and ter
        assert sec != primary
        assert ter != primary
        assert sec != ter
        assert CTXULTRA_SECONDARY[primary] == sec
        assert CTXULTRA_TERTIARY[primary] == ter


def test_given_triple_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    primary = list(range(1500))
    secondary = list(range(2000, 3500))
    tertiary = list(range(4000, 5500))
    q = [10, 20, 400, 800]
    meta = ctxultra_doc_meta(
        primary,
        secondary,
        tertiary,
        q,
        primary_source="a",
        secondary_source="b",
        tertiary_source="c",
    )
    assert meta["n_sources"] == 3
    assert meta["multi_source"] is True
    assert meta["k_slices"] == TOP_K_SLICES_ULTRA
    assert meta["n_slices"] == TOP_K_SLICES_ULTRA * 3
    assert meta["l_eff"] == 1500 + 1500 + 1500
    assert meta["ctx_bounded"] is True
    assert meta["sumcache_active"] <= ACTIVE_CAP
    assert meta["deeper_than_ctxmax_k"] is True


def test_given_ctx_ok_when_score_then_usable() -> None:
    meta = {
        "n_sources": 3,
        "l_eff": 50000,
        "sumcache_active": 352,
        "n_slices": 21,
        "k_slices": 7,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "primary_source": "a",
        "secondary_source": "b",
        "tertiary_source": "c",
    }
    score, err, notes, usable = score_ctxultra_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is False and usable is True
    assert any("sources=3" in n for n in notes)


def test_given_dual_source_when_score_then_not_usable() -> None:
    meta = {
        "n_sources": 2,
        "l_eff": 50000,
        "sumcache_active": 352,
        "n_slices": 14,
        "k_slices": 7,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "primary_source": "a",
        "secondary_source": "b",
        "tertiary_source": "c",
    }
    score, err, _notes, usable = score_ctxultra_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is True and usable is False


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = ctxultra_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=50000.0,
        mean_active=352.0,
        mean_slices=21.0,
        mean_sources=3.0,
        n_multi_source=10,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxultra(stats) == "PROMOTE"


def test_given_leff_not_up_when_decide_then_hold() -> None:
    stats = ctxultra_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=20000.0,
        mean_active=352.0,
        mean_slices=21.0,
        mean_sources=3.0,
        n_multi_source=10,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxultra(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxultra_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        [True] * 9 + [False],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        mean_l_eff=50000.0,
        mean_active=352.0,
        mean_slices=21.0,
        mean_sources=3.0,
        n_multi_source=10,
        n_fix=1,
    )
    assert decide_ctxultra(stats) == "KILL"
