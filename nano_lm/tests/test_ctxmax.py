"""Contract: Wave AE1 H-CTXMAX — multi-doc; L_eff↑ vs CTXPLUS."""

from __future__ import annotations

from ctxmax_ops import (
    ACTIVE_CAP,
    CTXMAX_ID,
    CTXMAX_N,
    CTXMAX_SECONDARY,
    CTXPLUS_MEAN_LEFF,
    MIN_SOURCES,
    MIN_USABLE,
    TOP_K_SLICES_MAX,
    ctxmax_doc_meta,
    ctxmax_stats,
    decide_ctxmax,
    score_ctxmax_trial,
    secondary_for,
)
from ctxplus_ops import TOP_K_SLICES


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AE1 H-CTXMAX
    assert CTXMAX_ID == "H-CTXMAX"
    assert CTXMAX_N == 10
    assert MIN_USABLE == 7
    assert MIN_SOURCES == 2
    assert TOP_K_SLICES_MAX == 5
    assert TOP_K_SLICES_MAX > TOP_K_SLICES
    assert CTXPLUS_MEAN_LEFF == 20522.6


def test_given_ae0_sources_when_secondary_then_all_mapped() -> None:
    from ae_session_ops import AE0_PACK

    for item in AE0_PACK:
        sec = secondary_for(item["source_id"])
        assert sec
        assert sec != item["source_id"]
        assert CTXMAX_SECONDARY[item["source_id"]] == sec


def test_given_dual_docs_when_meta_then_multi_source_and_deeper_k() -> None:
    primary = list(range(1500))
    secondary = list(range(2000, 3500))
    q = [10, 20, 400, 800]
    meta = ctxmax_doc_meta(
        primary,
        secondary,
        q,
        primary_source="a",
        secondary_source="b",
    )
    assert meta["n_sources"] == 2
    assert meta["multi_source"] is True
    assert meta["k_slices"] == TOP_K_SLICES_MAX
    assert meta["n_slices"] == TOP_K_SLICES_MAX * 2
    assert meta["l_eff"] == 1500 + 1500
    assert meta["ctx_bounded"] is True
    assert meta["sumcache_active"] <= ACTIVE_CAP
    assert meta["deeper_than_ctxplus_k"] is True


def test_given_ctx_ok_when_score_then_usable() -> None:
    meta = {
        "n_sources": 2,
        "l_eff": 40000,
        "sumcache_active": 352,
        "n_slices": 10,
        "k_slices": 5,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "primary_source": "a",
        "secondary_source": "b",
    }
    score, err, notes, usable = score_ctxmax_trial(
        mode="SEMWRAP_LOOKUP",
        completion="xprv / xpub",
        expected_gold="xprv / xpub",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is False and usable is True
    assert any("sources=2" in n for n in notes)


def test_given_single_source_when_score_then_not_usable() -> None:
    meta = {
        "n_sources": 1,
        "l_eff": 40000,
        "sumcache_active": 352,
        "n_slices": 5,
        "k_slices": 5,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "primary_source": "a",
        "secondary_source": "b",
    }
    score, err, _notes, usable = score_ctxmax_trial(
        mode="SEMWRAP_LOOKUP",
        completion="xprv",
        expected_gold="xprv",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is True and usable is False


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = ctxmax_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=31000.0,
        mean_active=352.0,
        mean_slices=10.0,
        mean_sources=2.0,
        n_multi_source=10,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxmax(stats) == "PROMOTE"


def test_given_leff_not_up_when_decide_then_hold() -> None:
    stats = ctxmax_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=10000.0,
        mean_active=352.0,
        mean_slices=10.0,
        mean_sources=2.0,
        n_multi_source=10,
        n_fix=0,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxmax(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxmax_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        [True] * 9 + [False],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        mean_l_eff=31000.0,
        mean_active=352.0,
        mean_slices=10.0,
        mean_sources=2.0,
        n_multi_source=10,
        n_fix=1,
    )
    assert decide_ctxmax(stats) == "KILL"
