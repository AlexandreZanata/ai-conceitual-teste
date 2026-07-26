"""Contract: Wave AJ3 H-SMARTPEAK — hepta cite + gen (pesquisa §3)."""

from __future__ import annotations

from smartpeak_ops import (
    MIN_CITE_OK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    SERVEALIGN_MEAN,
    SMARTPEAK_ID,
    SMARTPEAK_N,
    SMARTPEAK_PACK,
    SMARTPUSH_GEN_MEAN,
    decide_smartpeak,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_hepta_hop_cues,
    score_smartpeak_gen,
    score_smartpeak_lookup,
    smartpeak_stats,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AJ3 H-SMARTPEAK
    assert SMARTPEAK_ID == "H-SMARTPEAK"
    assert SMARTPEAK_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert MIN_CITE_OK == 8
    assert SMARTPUSH_GEN_MEAN == 4.0
    assert SERVEALIGN_MEAN == 3.4
    assert len(SMARTPEAK_PACK) == 10


def test_given_pack_when_paraphrase_then_differs_and_hepta() -> None:
    assert hard_paraphrase_ok(SMARTPEAK_PACK) is True
    assert has_adversarial_noise(SMARTPEAK_PACK) is True
    assert has_hepta_hop_cues(SMARTPEAK_PACK) is True
    for item in SMARTPEAK_PACK:
        assert item["id"].startswith("AJ-HITL-")
        assert item["septenary_source"]


def test_given_lookup_true_hit_when_score_then_cite() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, cited = score_smartpeak_lookup(
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


def test_given_gen_peak_exact_when_score_then_nine() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 50.0,
        "n_new": 32,
        "peak_used": True,
    }
    score, err, notes = score_smartpeak_gen(
        completion="32",
        expected_gold="32",
        payload=payload,
    )
    assert score == 9.0 and err is False
    assert any("SMARTPUSH" in n for n in notes)


def test_given_gen_periods_when_score_then_low() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 40.0,
        "n_new": 16,
        "peak_used": False,
    }
    score, err, _notes = score_smartpeak_gen(
        completion="........",
        expected_gold="anything",
        payload=payload,
    )
    assert score == 1.0 and err is True


def test_given_ready_stats_when_decide_then_promote() -> None:
    stats = smartpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        cite_flags=[True] * 10,
        gen_scores=[9.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_fix=0,
        n_peak=10,
    )
    assert stats["pass_gen"] is True
    assert stats["beats_smartpush_gen"] is True
    assert decide_smartpeak(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = smartpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        cite_flags=[True] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_fix=0,
        n_peak=0,
    )
    assert stats["pass_gen"] is False
    assert decide_smartpeak(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = smartpeak_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        cite_flags=[True] * 9 + [False],
        gen_scores=[9.0] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_fix=0,
        n_peak=10,
    )
    assert decide_smartpeak(stats) == "KILL"
