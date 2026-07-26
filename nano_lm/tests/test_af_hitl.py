"""Contract: Wave AF5 AF-HITL-10 — final pack mean≥7.0 · errors≤3."""

from __future__ import annotations

from af_hitl_ops import (
    AF5_ID,
    AF5_N,
    DECLARED_STACK,
    PASS_MAX_ERRORS,
    PASS_MEAN,
    STACK_CLAIM,
    af5_stats,
    claim_is_honest,
    decide_af5,
    score_af5_trial,
    select_app,
)


def test_given_contract_when_constants_then_match_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AF5 AF-HITL-10
    assert AF5_ID == "AF-HITL-10"
    assert AF5_N == 10
    assert PASS_MEAN == 7.0
    assert PASS_MAX_ERRORS == 3
    assert "H-CTXULTRA" in DECLARED_STACK
    assert "H-SMARTULTRA" in DECLARED_STACK
    assert "H-FASTULTRA" in DECLARED_STACK
    assert "H-APPULTRA" in DECLARED_STACK


def test_given_item_app_when_select_then_route() -> None:
    assert select_app("long-doc") == "app-longdoc"
    assert select_app("howto") == "app-howto"
    assert select_app("known-ask") == "app-known"


def test_given_stack_claim_when_check_then_honest() -> None:
    assert claim_is_honest(STACK_CLAIM) is True
    assert claim_is_honest("ship as open chat LM") is False


def test_given_true_hit_when_score_then_shippable() -> None:
    score, err, notes = score_af5_trial(
        mode="ASKFAST_CACHE",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        ctx_ok=True,
    )
    assert score == 9.0 and err is False
    assert any("AF5" in n for n in notes)


def test_given_ctx_fail_when_score_then_error() -> None:
    score, err, notes = score_af5_trial(
        mode="ASKFAST_CACHE",
        completion="BIP 9",
        expected_gold="BIP 9",
        lookup_kind="TRUE_HIT",
        ctx_ok=False,
    )
    assert score == 9.0 and err is True
    assert any("CTXULTRA_CTX_FAIL" in n for n in notes)


def test_given_pass_bar_when_decide_then_promote() -> None:
    stats = af5_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_fix=0,
        claim_ok=True,
        held_out_ok=True,
        n_known_app=3,
        n_long_app=2,
        n_howto_app=5,
    )
    assert stats["pass_bar"] is True
    assert decide_af5(stats) == "PROMOTE"


def test_given_overlap_when_decide_then_kill() -> None:
    stats = af5_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_fix=0,
        claim_ok=True,
        held_out_ok=False,
        n_known_app=3,
        n_long_app=2,
        n_howto_app=5,
    )
    assert decide_af5(stats) == "KILL"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = af5_stats(
        [9.0] * 9 + [0.0],
        [False] * 9 + [True],
        n_true_hit=9,
        n_false_hit=1,
        n_miss=0,
        n_fix=1,
        claim_ok=True,
        held_out_ok=True,
        n_known_app=3,
        n_long_app=2,
        n_howto_app=5,
    )
    assert decide_af5(stats) == "KILL"


def test_given_claim_bad_when_decide_then_hold() -> None:
    stats = af5_stats(
        [9.0] * 10,
        [False] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_miss=0,
        n_fix=0,
        claim_ok=False,
        held_out_ok=True,
        n_known_app=3,
        n_long_app=2,
        n_howto_app=5,
    )
    assert decide_af5(stats) == "HOLD"
