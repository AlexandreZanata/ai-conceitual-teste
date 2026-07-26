"""Contract: Wave AH6 AH-HITL-10 — final dual-arm lookup≥7 · gen≥5|HOLD."""

from __future__ import annotations

from ah_hitl_ops import (
    AH6_ID,
    AH6_N,
    DECLARED_STACK,
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    PASS_MAX_ERRORS,
    SHIP_CLAIM_AF,
    STACK_CLAIM,
    ah6_stats,
    claim_is_honest,
    decide_ah6,
    score_ah6_gen,
    score_ah6_lookup,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AH6 AH-HITL-10
    assert AH6_ID == "AH-HITL-10"
    assert AH6_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert PASS_MAX_ERRORS == 3
    assert "H-GENLIFT" in DECLARED_STACK
    assert "H-APPLIFT" in DECLARED_STACK
    assert "H-FASTLIFT" in DECLARED_STACK


def test_given_claims_when_check_then_honest() -> None:
    assert claim_is_honest(STACK_CLAIM) is True
    assert claim_is_honest(SHIP_CLAIM_AF) is True
    assert claim_is_honest("ship as open chat LM") is False


def test_given_lookup_true_hit_when_score_then_not_iq() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_ah6_lookup(
        mode="WRAP_LOOKUP",
        completion="gold",
        expected_gold="gold",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("not generative IQ" in n for n in notes)


def test_given_gen_zero_wall_when_score_then_error() -> None:
    payload = {"mode": "ASKFAST_CACHE", "wall_ms": 0.0, "n_new": 0}
    _score, err, notes = score_ah6_gen(
        completion="x",
        expected_gold="gold",
        payload=payload,
    )
    assert err is True
    assert any("wall_ms" in n for n in notes)


def test_given_lookup_and_gen_pass_when_decide_then_promote() -> None:
    stats = ah6_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_gen_wall_ok=10,
        n_fix=0,
        claim_ok=True,
        held_out_ok=True,
        n_known=3,
        n_howto=5,
        n_long=2,
    )
    assert stats["pass_lookup"] is True
    assert stats["pass_gen"] is True
    assert decide_ah6(stats) == "PROMOTE"


def test_given_lookup_ok_gen_low_when_decide_then_hold() -> None:
    stats = ah6_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[1.0] * 10,
        gen_errors=[True] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_gen_wall_ok=10,
        n_fix=0,
        claim_ok=True,
        held_out_ok=True,
        n_known=3,
        n_howto=5,
        n_long=2,
    )
    assert stats["pass_gen"] is False
    assert decide_ah6(stats) == "HOLD"


def test_given_false_hit_or_overlap_when_decide_then_kill() -> None:
    base = dict(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_gen_wall_ok=10,
        n_fix=0,
        claim_ok=True,
        held_out_ok=True,
        n_known=3,
        n_howto=5,
        n_long=2,
    )
    assert decide_ah6(ah6_stats(**base)) == "KILL"
    base["n_false_hit"] = 0
    base["n_true_hit"] = 10
    base["held_out_ok"] = False
    assert decide_ah6(ah6_stats(**base)) == "KILL"
