"""Contract: Wave AH1 H-GENLIFT — dual-arm gen lift (pesquisa §5)."""

from __future__ import annotations

from genlift_ops import (
    GENLIFT_ID,
    GENLIFT_N,
    GENLIFT_PACK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    SERVEALIGN_MEAN,
    SMARTREAL_GEN_MEAN,
    decide_genlift,
    genlift_stats,
    score_genlift_gen,
    score_genlift_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AH1 H-GENLIFT
    assert GENLIFT_ID == "H-GENLIFT"
    assert GENLIFT_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert SMARTREAL_GEN_MEAN == 4.0
    assert SERVEALIGN_MEAN == 3.4
    assert len(GENLIFT_PACK) == 10


def test_given_pack_when_ids_then_ah_hitl() -> None:
    for item in GENLIFT_PACK:
        assert item["id"].startswith("AH-HITL-")
        assert item["question"].strip()
        assert item["gold"].strip()
        assert item["source_id"]


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_genlift_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_gen_periods_when_score_then_low() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+ANTI_PERIOD",
        "wall_ms": 40.0,
        "n_new": 16,
    }
    score, err, notes = score_genlift_gen(
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
    score, err, notes = score_genlift_gen(
        completion="The heap stores variable size data at runtime.",
        expected_gold="On the heap.",
        payload=payload,
    )
    # Open-completion rubric: non-exact non-period → mid (4), not ASKSMART floor-5.
    assert score == 4.0 and err is True
    assert notes


def test_given_ready_gen_when_decide_then_promote() -> None:
    stats = genlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
    )
    assert stats["pass_gen"] is True
    assert stats["beats_smartreal_gen"] is True
    assert decide_genlift(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = genlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
    )
    assert stats["pass_gen"] is False
    assert decide_genlift(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = genlift_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_period=0,
        n_fix=0,
    )
    assert decide_genlift(stats) == "KILL"
