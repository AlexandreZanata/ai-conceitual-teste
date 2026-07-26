"""Contract: Wave AB3 H-LONGAPP — L_eff≫W on curated docs; ≥7/10 usable."""

from __future__ import annotations

from longapp_ops import (
    ACTIVE_CAP,
    LONGAPP_ID,
    LONGAPP_N,
    MIN_LEFF,
    MIN_LEFF_RATIO,
    MIN_USABLE,
    decide_longapp,
    longapp_doc_meta,
    longapp_stats,
    pick_best_roll_segment,
    score_longapp_trial,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.3 AB3 H-LONGAPP
    assert LONGAPP_ID == "H-LONGAPP"
    assert LONGAPP_N == 10
    assert MIN_USABLE == 7
    assert MIN_LEFF == 512
    assert MIN_LEFF_RATIO == 3.0


def test_given_long_ids_when_meta_then_leff_and_bounded() -> None:
    ids = list(range(900))
    q = [10, 20, 30]
    meta = longapp_doc_meta(ids, q)
    assert meta["l_eff"] == 900
    assert meta["l_eff_ok"] is True
    assert meta["ratio_ok"] is True
    assert meta["ctx_bounded"] is True
    assert meta["sumcache_active"] <= ACTIVE_CAP


def test_given_short_ids_when_meta_then_leff_fail() -> None:
    ids = list(range(100))
    meta = longapp_doc_meta(ids, [1, 2])
    assert meta["l_eff_ok"] is False


def test_given_question_tokens_when_pick_roll_then_overlap() -> None:
    # Place distinctive tokens in segment 2 window.
    ids = [0] * 256 + [99, 98, 97] + [0] * 200
    seg = pick_best_roll_segment(ids, [99, 98, 97])
    assert seg["overlap"] > 0.0
    assert 99 in seg["ctx_ids"]


def test_given_ctx_ok_when_score_then_usable() -> None:
    meta = {
        "l_eff": 900,
        "sumcache_active": 352,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "ratio_vs_roll_w": 7.0,
    }
    score, err, notes, usable = score_longapp_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is False and usable is True
    assert any("L_eff=" in n for n in notes)


def test_given_ctx_fail_when_score_then_not_usable() -> None:
    meta = {
        "l_eff": 100,
        "sumcache_active": 100,
        "l_eff_ok": False,
        "ratio_ok": False,
        "ctx_bounded": True,
        "ratio_vs_roll_w": 0.5,
    }
    score, err, _notes, usable = score_longapp_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is True and usable is False


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = longapp_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=2000.0,
        mean_active=352.0,
        mean_ratio=15.0,
    )
    assert decide_longapp(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = longapp_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        [True] * 9 + [False],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        mean_l_eff=2000.0,
        mean_active=352.0,
        mean_ratio=15.0,
    )
    assert decide_longapp(stats) == "KILL"


def test_given_few_usable_when_decide_then_hold() -> None:
    usables = [True] * 6 + [False] * 4
    stats = longapp_stats(
        [9.0] * 6 + [4.0] * 4,
        [False] * 6 + [True] * 4,
        usables,
        n_true_hit=6,
        n_false_hit=0,
        n_miss=4,
        mean_l_eff=2000.0,
        mean_active=352.0,
        mean_ratio=15.0,
    )
    assert decide_longapp(stats) == "HOLD"
