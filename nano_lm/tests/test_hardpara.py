"""Contract: Wave AD1 H-HARDPARA — adversarial para; mean≥7; false-hit≈0."""

from __future__ import annotations

from hardpara_ops import (
    HARDPARA_ID,
    HARDPARA_N,
    HARDPARA_PACK,
    MIN_MEAN,
    decide_hardpara,
    hard_paraphrase_ok,
    hardpara_stats,
    has_adversarial_noise,
    paraphrase_collides_parents,
    route_hardpara,
    score_hardpara_trial,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §8.6 / §13.1 AD1 H-HARDPARA
    assert HARDPARA_ID == "H-HARDPARA"
    assert HARDPARA_N == 10
    assert MIN_MEAN == 7.0
    assert len(HARDPARA_PACK) == 10


def test_given_pack_when_paraphrase_then_harder_than_parent() -> None:
    assert hard_paraphrase_ok(HARDPARA_PACK) is True
    assert paraphrase_collides_parents(HARDPARA_PACK) == []


def test_given_pack_when_noise_then_adversarial_cues() -> None:
    assert has_adversarial_noise(HARDPARA_PACK) is True


def test_given_pack_when_ids_then_match_ad0() -> None:
    for item in HARDPARA_PACK:
        assert item["id"].startswith("AD-HITL-")
        assert item["gold"].strip()
        assert item["paraphrase"].strip()
        assert item["source_id"]


def test_given_wrap_mode_when_route_then_semwrap() -> None:
    text, route = route_hardpara(" BIP 9. ", mode="SEMWRAP_LOOKUP")
    assert text == "BIP 9"
    assert route == "SEMWRAP_ROUTE"


def test_given_periods_when_route_then_block() -> None:
    _text, route = route_hardpara("........", mode="OPEN")
    assert route == "PERIOD_BLOCK"


def test_given_true_hit_when_score_then_nine() -> None:
    score, err, notes = score_hardpara_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        route="SEMWRAP_ROUTE",
    )
    assert score == 9.0 and err is False
    assert any("route=" in n for n in notes)


def test_given_false_hit_when_score_then_zero() -> None:
    score, err, _ = score_hardpara_trial(
        mode="SEMWRAP_LOOKUP",
        completion="wrong",
        expected_gold="BIP 9",
        lookup_kind="FALSE_HIT",
        route="SEMWRAP_ROUTE",
    )
    assert score == 0.0 and err is True


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = hardpara_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=0,
    )
    assert decide_hardpara(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = hardpara_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=1,
    )
    assert decide_hardpara(stats) == "KILL"


def test_given_soft_mean_when_decide_then_hold() -> None:
    stats = hardpara_stats(
        [6.0] * 10,
        [True] * 10,
        n_true_hit=0,
        n_false_hit=0,
        n_miss=10,
        n_semwrap_route=0,
        n_fix=0,
    )
    assert stats["pass_mean"] is False
    assert decide_hardpara(stats) == "HOLD"
