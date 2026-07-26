"""Contract: Wave AE2 H-SMARTMAX — multi-hop cite; mean≥7; false-hit≈0."""

from __future__ import annotations

from smartmax_ops import (
    MIN_CITE_OK,
    MIN_MEAN,
    SMARTMAX_ID,
    SMARTMAX_N,
    SMARTMAX_PACK,
    cite_ok,
    decide_smartmax,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_multihop_cues,
    paraphrase_collides_parents,
    route_smartmax,
    score_smartmax_trial,
    smartmax_stats,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AE2 H-SMARTMAX
    assert SMARTMAX_ID == "H-SMARTMAX"
    assert SMARTMAX_N == 10
    assert MIN_MEAN == 7.0
    assert MIN_CITE_OK == 7
    assert len(SMARTMAX_PACK) == 10


def test_given_pack_when_paraphrase_then_harder_than_parent() -> None:
    assert hard_paraphrase_ok(SMARTMAX_PACK) is True
    assert paraphrase_collides_parents(SMARTMAX_PACK) == []


def test_given_pack_when_noise_then_adversarial_and_multihop() -> None:
    assert has_adversarial_noise(SMARTMAX_PACK) is True
    assert has_multihop_cues(SMARTMAX_PACK) is True


def test_given_pack_when_ids_then_match_ae0_with_secondary() -> None:
    from ctxmax_ops import secondary_for

    for item in SMARTMAX_PACK:
        assert item["id"].startswith("AE-HITL-")
        assert item["gold"].strip()
        assert item["paraphrase"].strip()
        assert item["source_id"]
        assert item["secondary_source"] == secondary_for(item["source_id"])


def test_given_wrap_mode_when_route_then_semwrap() -> None:
    text, route = route_smartmax(" xprv / xpub. ", mode="SEMWRAP_LOOKUP")
    assert text == "xprv / xpub"
    assert route == "SEMWRAP_ROUTE"


def test_given_true_hit_primary_when_cite_then_ok() -> None:
    assert (
        cite_ok(
            expected_source_id="bip-0032",
            hit_source_id="bip-0032",
            lookup_kind="TRUE_HIT",
        )
        is True
    )
    assert (
        cite_ok(
            expected_source_id="bip-0032",
            hit_source_id="bip-0039",
            lookup_kind="TRUE_HIT",
        )
        is False
    )


def test_given_true_hit_when_score_then_nine_and_cite() -> None:
    score, err, notes, cited = score_smartmax_trial(
        mode="SEMWRAP_LOOKUP",
        completion="xprv / xpub",
        expected_gold="xprv / xpub",
        lookup_kind="TRUE_HIT",
        route="SEMWRAP_ROUTE",
        expected_source_id="bip-0032",
        hit_source_id="bip-0032",
    )
    assert score == 9.0 and err is False and cited is True
    assert any("cite_ok=True" in n for n in notes)


def test_given_wrong_cite_when_score_then_error() -> None:
    score, err, _notes, cited = score_smartmax_trial(
        mode="SEMWRAP_LOOKUP",
        completion="xprv / xpub",
        expected_gold="xprv / xpub",
        lookup_kind="TRUE_HIT",
        route="SEMWRAP_ROUTE",
        expected_source_id="bip-0032",
        hit_source_id="bip-0039",
    )
    assert score == 9.0 and err is True and cited is False


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = smartmax_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=0,
    )
    assert decide_smartmax(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = smartmax_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        [True] * 9 + [False],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=1,
    )
    assert decide_smartmax(stats) == "KILL"


def test_given_weak_cite_when_decide_then_hold() -> None:
    stats = smartmax_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 6 + [False] * 4,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=0,
    )
    assert stats["pass_cite"] is False
    assert decide_smartmax(stats) == "HOLD"
