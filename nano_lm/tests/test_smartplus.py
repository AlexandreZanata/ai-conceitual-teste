"""Contract: Wave AC2 H-SMARTPLUS — hard paraphrases; mean≥7; false-hit≈0."""

from __future__ import annotations

from smartplus_ops import (
    MIN_MEAN,
    SMARTPLUS_ID,
    SMARTPLUS_N,
    SMARTPLUS_PACK,
    decide_smartplus,
    hard_paraphrase_ok,
    paraphrase_collides_parents,
    route_smartplus,
    score_smartplus_trial,
    smartplus_stats,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.5 / §12.1 AC2 H-SMARTPLUS
    assert SMARTPLUS_ID == "H-SMARTPLUS"
    assert SMARTPLUS_N == 10
    assert MIN_MEAN == 7.0
    assert len(SMARTPLUS_PACK) == 10


def test_given_pack_when_paraphrase_then_harder_than_parent() -> None:
    assert hard_paraphrase_ok(SMARTPLUS_PACK) is True
    assert paraphrase_collides_parents(SMARTPLUS_PACK) == []


def test_given_pack_when_ids_then_match_ac0() -> None:
    for item in SMARTPLUS_PACK:
        assert item["id"].startswith("AC-HITL-")
        assert item["gold"].strip()
        assert item["paraphrase"].strip()
        assert item["source_id"]


def test_given_wrap_mode_when_route_then_semwrap() -> None:
    text, route = route_smartplus(" BIP 9. ", mode="SEMWRAP_LOOKUP")
    assert text == "BIP 9"
    assert route == "SEMWRAP_ROUTE"


def test_given_periods_when_route_then_block() -> None:
    _text, route = route_smartplus("........", mode="OPEN")
    assert route == "PERIOD_BLOCK"


def test_given_true_hit_when_score_then_nine() -> None:
    score, err, notes = score_smartplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        route="SEMWRAP_ROUTE",
    )
    assert score == 9.0 and err is False
    assert any("route=" in n for n in notes)


def test_given_false_hit_when_score_then_zero() -> None:
    score, err, _ = score_smartplus_trial(
        mode="SEMWRAP_LOOKUP",
        completion="wrong",
        expected_gold="BIP 9",
        lookup_kind="FALSE_HIT",
        route="SEMWRAP_ROUTE",
    )
    assert score == 0.0 and err is True


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = smartplus_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=0,
    )
    assert decide_smartplus(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = smartplus_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=1,
    )
    assert decide_smartplus(stats) == "KILL"


def test_given_soft_mean_when_decide_then_hold() -> None:
    stats = smartplus_stats(
        [6.0] * 10,
        [True] * 10,
        n_true_hit=0,
        n_false_hit=0,
        n_miss=10,
        n_semwrap_route=0,
        n_fix=0,
    )
    assert stats["pass_mean"] is False
    assert decide_smartplus(stats) == "HOLD"
