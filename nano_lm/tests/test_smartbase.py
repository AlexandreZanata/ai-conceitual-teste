"""Contract: Wave AP3 H-SMARTBASE — trideca cite + gen (pesquisa §3)."""

from __future__ import annotations

from smartbase_ops import (
    GENBASE_ABLATED_GEN_MEAN,
    MIN_CITE_OK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    SERVEALIGN_MEAN,
    SMARTBASE_ID,
    SMARTBASE_N,
    SMARTBASE_PACK,
    SMARTCORE_GEN_MEAN,
    decide_smartbase,
    hard_paraphrase_ok,
    has_adversarial_noise,
    has_trideca_hop_cues,
    score_smartbase_gen,
    score_smartbase_lookup,
    smartbase_stats,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §3 AP3 H-SMARTBASE
    assert SMARTBASE_ID == "H-SMARTBASE"
    assert SMARTBASE_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert MIN_CITE_OK == 8
    assert SMARTCORE_GEN_MEAN == 9.0
    assert GENBASE_ABLATED_GEN_MEAN == 4.0
    assert SERVEALIGN_MEAN == 3.4
    assert len(SMARTBASE_PACK) == 10


def test_given_pack_when_paraphrase_then_differs_and_trideca() -> None:
    assert hard_paraphrase_ok(SMARTBASE_PACK) is True
    assert has_adversarial_noise(SMARTBASE_PACK) is True
    assert has_trideca_hop_cues(SMARTBASE_PACK) is True
    for item in SMARTBASE_PACK:
        assert item["id"].startswith("AP-HITL-")
        assert item["tredenary_source"]


def test_given_lookup_true_hit_when_score_then_cite() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes, cited = score_smartbase_lookup(
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
    score, err, notes, cited = score_smartbase_lookup(
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


def test_given_gen_struct_update_dots_when_score_then_nine() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 50.0,
        "n_new": 4,
        "peak_used": True,
    }
    score, err, notes = score_smartbase_gen(
        completion="..",
        expected_gold="..",
        payload=payload,
    )
    assert score == 9.0 and err is False
    assert any("struct-update" in n for n in notes)

    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 50.0,
        "n_new": 32,
        "peak_used": True,
    }
    score, err, notes = score_smartbase_gen(
        completion="21",
        expected_gold="21",
        payload=payload,
    )
    assert score == 9.0 and err is False
    assert any("GENBASE" in n for n in notes)
    assert any("SMARTCORE" in n for n in notes)


def test_given_gen_periods_when_score_then_low() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+PEAK",
        "wall_ms": 40.0,
        "n_new": 16,
        "peak_used": False,
    }
    score, err, _notes = score_smartbase_gen(
        completion="........",
        expected_gold="anything",
        payload=payload,
    )
    assert score == 1.0 and err is True


def test_given_ready_stats_when_decide_then_promote() -> None:
    stats = smartbase_stats(
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
    assert stats["beats_genbase_ablated"] is True
    assert stats["peers_smartcore_gen"] is True
    assert stats["trideca_hop"] is True
    assert decide_smartbase(stats) == "PROMOTE"


def test_given_low_gen_when_decide_then_hold() -> None:
    stats = smartbase_stats(
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
    assert decide_smartbase(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = smartbase_stats(
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
    assert decide_smartbase(stats) == "KILL"
