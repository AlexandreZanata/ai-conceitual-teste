"""Contract: Wave AF2 H-SMARTULTRA — triple-hop cite; mean≥7; false-hit≈0."""

from __future__ import annotations

from smartultra_ops import (
    MIN_CITE_OK,
    MIN_MEAN,
    SMARTULTRA_ID,
    SMARTULTRA_N,
    SMARTULTRA_PACK,
    cite_ok,
    decide_smartultra,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_triple_hop_cues,
    paraphrase_collides_parents,
    route_smartultra,
    score_smartultra_trial,
    smartultra_stats,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF2 H-SMARTULTRA
    assert SMARTULTRA_ID == "H-SMARTULTRA"
    assert SMARTULTRA_N == 10
    assert MIN_MEAN == 7.0
    assert MIN_CITE_OK == 8
    assert MIN_CITE_OK > 7
    assert len(SMARTULTRA_PACK) == 10


def test_given_pack_when_paraphrase_then_harder_than_parent() -> None:
    assert hard_paraphrase_ok(SMARTULTRA_PACK) is True
    assert paraphrase_collides_parents(SMARTULTRA_PACK) == []


def test_given_pack_when_noise_then_adversarial_and_triple_hop() -> None:
    assert has_adversarial_noise(SMARTULTRA_PACK) is True
    assert has_triple_hop_cues(SMARTULTRA_PACK) is True


def test_given_pack_when_ids_then_match_af0_with_sec_ter() -> None:
    from ctxultra_ops import secondary_for, tertiary_for

    for item in SMARTULTRA_PACK:
        assert item["id"].startswith("AF-HITL-")
        assert item["gold"].strip()
        assert item["paraphrase"].strip()
        assert item["source_id"]
        assert item["secondary_source"] == secondary_for(item["source_id"])
        assert item["tertiary_source"] == tertiary_for(item["source_id"])
        assert item["secondary_source"] != item["tertiary_source"]


def test_given_wrap_mode_when_route_then_semwrap() -> None:
    text, route = route_smartultra(
        " BIP 9 (version-bits). ", mode="SEMWRAP_LOOKUP"
    )
    assert "BIP 9" in text
    assert route == "SEMWRAP_ROUTE"


def test_given_true_hit_primary_when_cite_then_ok() -> None:
    assert (
        cite_ok(
            expected_source_id="bip-0001",
            hit_source_id="bip-0001",
            lookup_kind="TRUE_HIT",
        )
        is True
    )
    assert (
        cite_ok(
            expected_source_id="bip-0001",
            hit_source_id="bip-0032",
            lookup_kind="TRUE_HIT",
        )
        is False
    )


def test_given_true_hit_when_score_then_nine_and_cite() -> None:
    score, err, notes, cited = score_smartultra_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        route="SEMWRAP_ROUTE",
        expected_source_id="bitcoin-doc-bips",
        hit_source_id="bitcoin-doc-bips",
    )
    assert score == 9.0 and err is False and cited is True
    assert any("cite_ok=True" in n for n in notes)


def test_given_wrong_cite_when_score_then_error() -> None:
    score, err, _notes, cited = score_smartultra_trial(
        mode="SEMWRAP_LOOKUP",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        route="SEMWRAP_ROUTE",
        expected_source_id="bitcoin-doc-bips",
        hit_source_id="bip-0001",
    )
    assert score == 9.0 and err is True and cited is False


def test_given_good_stats_when_decide_then_promote() -> None:
    stats = smartultra_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=0,
    )
    assert stats["beyond_smartmax_cite_bar"] is True
    assert decide_smartultra(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = smartultra_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        [True] * 9 + [False],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=1,
    )
    assert decide_smartultra(stats) == "KILL"


def test_given_weak_cite_when_decide_then_hold() -> None:
    stats = smartultra_stats(
        [9.0] * 10,
        [False] * 10,
        [True] * 7 + [False] * 3,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_semwrap_route=10,
        n_fix=0,
    )
    assert stats["pass_cite"] is False
    assert decide_smartultra(stats) == "HOLD"
