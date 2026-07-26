"""Contract: Wave AH3 H-SMARTLIFT — penta cite + gen (pesquisa §5)."""

from __future__ import annotations

from smartlift_ops import (
    MIN_CITE_OK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    SERVEALIGN_MEAN,
    SMARTLIFT_ID,
    SMARTLIFT_N,
    SMARTLIFT_PACK,
    SMARTREAL_GEN_MEAN,
    decide_smartlift,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_penta_hop_cues,
    score_smartlift_gen,
    score_smartlift_lookup,
    smartlift_stats,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AH3 H-SMARTLIFT
    assert SMARTLIFT_ID == "H-SMARTLIFT"
    assert SMARTLIFT_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert MIN_CITE_OK == 8
    assert SMARTREAL_GEN_MEAN == 4.0
    assert SERVEALIGN_MEAN == 3.4
    assert len(SMARTLIFT_PACK) == 10


def test_given_pack_when_paraphrase_then_differs_and_noisy() -> None:
    assert hard_paraphrase_ok(SMARTLIFT_PACK) is True
    assert has_adversarial_noise(SMARTLIFT_PACK) is True
    assert has_penta_hop_cues(SMARTLIFT_PACK) is True


def test_given_lookup_true_hit_when_score_then_cite() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, cited = score_smartlift_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        expected_source_id="bip-0039",
        hit_source_id="bip-0039",
        payload=payload,
    )
    assert score >= 8.0 and err is False and cited is True
    assert any("not generative IQ" in n for n in notes)


def test_given_gen_periods_when_score_then_low() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+ANTI_PERIOD",
        "wall_ms": 40.0,
        "n_new": 16,
    }
    score, err, notes = score_smartlift_gen(
        completion="........",
        expected_gold="anything",
        payload=payload,
    )
    assert score == 1.0 and err is True
    assert notes


def test_given_gen_substance_when_score_then_open_mid() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+ANTI_PERIOD",
        "wall_ms": 50.0,
        "n_new": 32,
    }
    score, err, notes = score_smartlift_gen(
        completion="The heap stores variable size data at runtime.",
        expected_gold="On the heap.",
        payload=payload,
    )
    assert score == 4.0 and err is True
    assert notes


def test_given_ready_gen_when_decide_then_promote() -> None:
    stats = smartlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        cite_flags=[True] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_fix=0,
    )
    assert stats["pass_gen"] is True
    assert decide_smartlift(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = smartlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        cite_flags=[True] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_fix=0,
    )
    assert stats["pass_gen"] is False
    assert decide_smartlift(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = smartlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        cite_flags=[True] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_fix=0,
    )
    assert decide_smartlift(stats) == "KILL"
