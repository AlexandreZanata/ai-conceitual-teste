"""Contract: Wave AL3 H-SMARTFRESH — nona cite + gen (pesquisa §3)."""

from __future__ import annotations

from smartfresh_ops import (
    MIN_CITE_OK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    SERVEALIGN_MEAN,
    SMARTFRESH_ID,
    SMARTFRESH_N,
    SMARTFRESH_PACK,
    SMARTMORE_GEN_MEAN,
    SMARTPUSH_GEN_MEAN,
    decide_smartfresh,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_nona_hop_cues,
    score_smartfresh_gen,
    score_smartfresh_lookup,
    smartfresh_stats,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AL3 H-SMARTFRESH
    assert SMARTFRESH_ID == "H-SMARTFRESH"
    assert SMARTFRESH_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert MIN_CITE_OK == 8
    assert SMARTMORE_GEN_MEAN == 9.0
    assert SMARTPUSH_GEN_MEAN == 4.0
    assert SERVEALIGN_MEAN == 3.4
    assert len(SMARTFRESH_PACK) == 10


def test_given_pack_when_paraphrase_then_differs_and_nona() -> None:
    assert hard_paraphrase_ok(SMARTFRESH_PACK) is True
    assert has_adversarial_noise(SMARTFRESH_PACK) is True
    assert has_nona_hop_cues(SMARTFRESH_PACK) is True
    for item in SMARTFRESH_PACK:
        assert item["id"].startswith("AL-HITL-")
        assert item["nonary_source"]


def test_given_lookup_true_hit_when_score_then_cite() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, cited = score_smartfresh_lookup(
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


def test_given_false_hit_when_score_then_error() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, cited = score_smartfresh_lookup(
        mode="WRAP_LOOKUP",
        completion="wrong",
        expected_gold="gold",
        lookup_kind="FALSE_HIT",
        expected_source_id="bip-0039",
        hit_source_id="bip-0032",
        payload=payload,
    )
    assert err is True and cited is False
    assert any("false-neighbor" in n.lower() or "FP" in n for n in notes)
    assert score <= 4.0


def test_given_gen_peak_exact_when_score_then_nine() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 50.0,
        "n_new": 32,
        "peak_used": True,
    }
    score, err, notes = score_smartfresh_gen(
        completion="24",
        expected_gold="24",
        payload=payload,
    )
    assert score == 9.0 and err is False
    assert any("SMARTPUSH" in n for n in notes)
    assert any("SMARTMORE" in n for n in notes)


def test_given_gen_periods_when_score_then_low() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 40.0,
        "n_new": 16,
        "peak_used": False,
    }
    score, err, _notes = score_smartfresh_gen(
        completion="........",
        expected_gold="anything",
        payload=payload,
    )
    assert score == 1.0 and err is True


def test_given_ready_stats_when_decide_then_promote() -> None:
    stats = smartfresh_stats(
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
    assert stats["peers_smartmore_gen"] is True
    assert stats["nona_hop"] is True
    assert decide_smartfresh(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = smartfresh_stats(
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
    assert decide_smartfresh(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = smartfresh_stats(
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
    assert decide_smartfresh(stats) == "KILL"
