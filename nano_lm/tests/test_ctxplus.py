"""Contract: Wave AC1 H-CTXPLUS — multi-slice; L_eff↑ vs AB LONGAPP."""

from __future__ import annotations

from ctxplus_ops import (
    AB_LONGAPP_MEAN_LEFF,
    ACTIVE_CAP,
    CTXPLUS_ID,
    CTXPLUS_N,
    MIN_LEFF,
    MIN_LEFF_RATIO,
    MIN_USABLE,
    TOP_K_SLICES,
    ctxplus_doc_meta,
    ctxplus_stats,
    decide_ctxplus,
    pick_top_roll_segments,
    score_ctxplus_trial,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.5 / §12.1 AC1 H-CTXPLUS
    assert CTXPLUS_ID == "H-CTXPLUS"
    assert CTXPLUS_N == 10
    assert MIN_USABLE == 7
    assert TOP_K_SLICES == 3
    assert MIN_LEFF == 512
    assert MIN_LEFF_RATIO == 3.0
    assert AB_LONGAPP_MEAN_LEFF == 10544.9


def test_given_long_ids_when_meta_then_multi_slice() -> None:
    ids = list(range(1200))
    q = [10, 20, 30, 400, 800]
    meta = ctxplus_doc_meta(ids, q)
    assert meta["l_eff"] == 1200
    assert meta["n_slices"] == TOP_K_SLICES
    assert meta["l_eff_ok"] is True
    assert meta["ratio_ok"] is True
    assert meta["ctx_bounded"] is True
    assert meta["sumcache_active"] <= ACTIVE_CAP
    assert meta["slice_union"] >= meta["best_slice_active"]


def test_given_question_tokens_when_top_slices_then_ranked() -> None:
    ids = [0] * 256 + [99, 98, 97] + [0] * 200 + [50, 51] + [0] * 200
    segs = pick_top_roll_segments(ids, [99, 98, 97], k=2)
    assert len(segs) == 2
    assert segs[0]["overlap"] >= segs[1]["overlap"]
    assert 99 in segs[0]["ctx_ids"]


def test_given_ctx_ok_when_score_then_usable() -> None:
    meta = {
        "l_eff": 20000,
        "sumcache_active": 352,
        "n_slices": 3,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "slice_union": 400,
    }
    score, err, notes, usable = score_ctxplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is False and usable is True
    assert any("slices=" in n for n in notes)


def test_given_no_slices_when_score_then_not_usable() -> None:
    meta = {
        "l_eff": 20000,
        "sumcache_active": 352,
        "n_slices": 0,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "slice_union": 0,
    }
    score, err, _notes, usable = score_ctxplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is True and usable is False


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = ctxplus_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=20000.0,
        mean_active=352.0,
        mean_ratio=150.0,
        mean_slices=3.0,
        mean_union=400.0,
        n_multi_deeper=8,
    )
    assert stats["pass_leff_up"] is True
    assert decide_ctxplus(stats) == "PROMOTE"


def test_given_leff_not_up_when_decide_then_hold() -> None:
    stats = ctxplus_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=8000.0,
        mean_active=352.0,
        mean_ratio=60.0,
        mean_slices=3.0,
        mean_union=400.0,
        n_multi_deeper=5,
    )
    assert stats["pass_leff_up"] is False
    assert decide_ctxplus(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = ctxplus_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        [True] * 9 + [False],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        mean_l_eff=20000.0,
        mean_active=352.0,
        mean_ratio=150.0,
        mean_slices=3.0,
        mean_union=400.0,
        n_multi_deeper=8,
    )
    assert decide_ctxplus(stats) == "KILL"
