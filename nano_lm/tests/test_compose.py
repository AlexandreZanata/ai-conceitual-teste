"""Contract: Wave AD2 H-COMPOSE — multi-source CTXPLUS; usable≥7/10."""

from __future__ import annotations

from compose_ops import (
    COMPOSE_ID,
    COMPOSE_N,
    COMPOSE_SECONDARY,
    MIN_SOURCES,
    MIN_USABLE,
    compose_doc_meta,
    compose_stats,
    decide_compose,
    score_compose_trial,
    secondary_for,
)
from ctxplus_ops import ACTIVE_CAP


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.6 / §13.1 AD2 H-COMPOSE
    assert COMPOSE_ID == "H-COMPOSE"
    assert COMPOSE_N == 10
    assert MIN_USABLE == 7
    assert MIN_SOURCES == 2
    assert len(COMPOSE_SECONDARY) == 10


def test_given_ad0_sources_when_secondary_then_distinct() -> None:
    for primary, secondary in COMPOSE_SECONDARY.items():
        assert secondary_for(primary) == secondary
        assert primary != secondary


def test_given_two_docs_when_meta_then_multi_source() -> None:
    primary = list(range(800))
    secondary = list(range(800, 2000))
    q = [10, 20, 900]
    meta = compose_doc_meta(
        primary,
        secondary,
        q,
        primary_source="a",
        secondary_source="b",
    )
    assert meta["n_sources"] == 2
    assert meta["multi_source"] is True
    assert meta["l_eff"] == 800 + 1200
    assert meta["n_slices"] >= 2
    assert meta["sumcache_active"] <= ACTIVE_CAP
    assert meta["l_eff_ok"] is True


def test_given_ctx_ok_when_score_then_usable() -> None:
    meta = {
        "n_sources": 2,
        "l_eff": 20000,
        "sumcache_active": 352,
        "n_slices": 6,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "primary_source": "a",
        "secondary_source": "b",
    }
    score, err, notes, usable = score_compose_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is False and usable is True
    assert any("sources=2" in n for n in notes)


def test_given_single_source_when_score_then_not_usable() -> None:
    meta = {
        "n_sources": 1,
        "l_eff": 20000,
        "sumcache_active": 352,
        "n_slices": 3,
        "l_eff_ok": True,
        "ratio_ok": True,
        "ctx_bounded": True,
        "primary_source": "a",
        "secondary_source": "b",
    }
    score, err, _notes, usable = score_compose_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        meta=meta,
    )
    assert score == 9.0 and err is True and usable is False


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = compose_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=20000.0,
        mean_active=352.0,
        mean_slices=6.0,
        mean_sources=2.0,
        n_multi_source=10,
        n_fix=0,
    )
    assert decide_compose(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = compose_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        [True] * 9 + [False],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        mean_l_eff=20000.0,
        mean_active=352.0,
        mean_slices=6.0,
        mean_sources=2.0,
        n_multi_source=9,
        n_fix=1,
    )
    assert decide_compose(stats) == "KILL"


def test_given_low_usable_when_decide_then_hold() -> None:
    stats = compose_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 6 + [False] * 4,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        mean_l_eff=20000.0,
        mean_active=352.0,
        mean_slices=6.0,
        mean_sources=2.0,
        n_multi_source=6,
        n_fix=0,
    )
    assert stats["pass_usable"] is False
    assert decide_compose(stats) == "HOLD"
