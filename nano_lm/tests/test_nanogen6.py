"""Contract: Wave AV3 H-NANOGEN6 — true continue; span-fallback ≠ gen IQ."""

from __future__ import annotations

from nanogen6_ops import (
    MIN_LOOKUP_MEAN,
    MIN_TRUE_CONTINUE_MEAN,
    NANOGEN6_HYPOTHESIS,
    NANOGEN6_ID,
    NANOGEN6_N,
    NANOGEN6_PACK,
    NANOGEN6_THESIS,
    PARENT_NANOGEN5_STRICT,
    apply_refuse_or_continue,
    decide_nanogen6,
    nanogen6_stats,
    score_nanogen6_gen,
    score_nanogen6_lookup,
)


def test_given_contract_when_constants_then_match_av3_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AV3 — true_continue≥5.5 else HOLD
    assert NANOGEN6_ID == "H-NANOGEN6"
    assert NANOGEN6_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_TRUE_CONTINUE_MEAN == 5.5
    assert PARENT_NANOGEN5_STRICT == 5.5
    assert len(NANOGEN6_PACK) == 10
    hyp = NANOGEN6_HYPOTHESIS.lower()
    assert "true_continue" in hyp or "refuse-or-continue" in hyp
    assert "span" in hyp or "truncate" in hyp
    assert "fallback" in hyp
    assert "nanogen5" in hyp or "5.5" in NANOGEN6_HYPOTHESIS
    assert "clone" in hyp
    assert "true continue" in NANOGEN6_THESIS.lower() or "refuse" in NANOGEN6_THESIS.lower()


def test_given_pack_when_kinds_then_held_and_para() -> None:
    kinds = [p["kind"] for p in NANOGEN6_PACK]
    assert kinds.count("held-out") == 5
    assert kinds.count("paraphrase") == 5


def test_given_gibberish_tail_when_refuse_or_continue_then_span_fallback() -> None:
    text = (
        "CS = ENT / 32 Once upon a time there was a little story "
        "looking for everything really quickly"
    )
    out, kind, trunc, refuse = apply_refuse_or_continue(
        text=text, prefix="CS = ENT / 32"
    )
    assert kind == "span_fallback"
    assert trunc is True and refuse is False
    assert out == "CS = ENT / 32"


def test_given_seed_only_when_refuse_or_continue_then_span_fallback() -> None:
    out, kind, trunc, refuse = apply_refuse_or_continue(
        text="CS = ENT / 32", prefix="CS = ENT / 32"
    )
    assert kind == "span_fallback"
    assert trunc is True
    assert refuse is False
    assert out == "CS = ENT / 32"


def test_given_span_fallback_when_score_then_zero_gen_credit() -> None:
    # GIVEN truncated-to-span that would pass NANOGEN5 STRICT F1
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": False,
        "snippet_prefix": True,
        "continue_kind": "span_fallback",
        "span_fallback": True,
        "gibberish_tail_truncated": True,
        "product_mode": "PEAK",
    }
    score, err, notes = score_nanogen6_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("span-fallback" in n.lower() or "≠ gen" in n for n in notes)


def test_given_true_continue_when_f1_high_then_pass() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 12.0,
        "n_new": 16,
        "peak_used": False,
        "bank_grounded": False,
        "snippet_prefix": True,
        "continue_kind": "true_continue",
        "span_fallback": False,
        "product_mode": "DECODE",
    }
    score, err, notes = score_nanogen6_gen(
        completion=(
            "CS = ENT / 32 is the BIP-39 checksum relation for "
            "mnemonic entropy length."
        ),
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score >= 5.5 and err is False
    assert any("true-gen" in n.lower() or "f1" in n.lower() for n in notes)


def test_given_only_span_fallback_wins_when_stats_then_hold() -> None:
    # Simulate NANOGEN5-style truncate wins: all gen credit from span_fallback
    stats = nanogen6_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 7 + [4.0] * 3,  # truncates scored 4.0 under N6
        gen_errors=[True] * 10,
        gen_peak_scores=[9.0] * 10,
        gen_bank_scores=[9.0] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
        n_bank_grounded=0,
        n_abstain=7,
        n_snippet_prefix=10,
        n_span_fallback=3,
        n_true_continue=0,
    )
    assert stats["pass_gen"] is False
    assert stats["n_span_fallback"] == 3
    assert stats["n_true_continue"] == 0
    assert decide_nanogen6(stats) == "HOLD"


def test_given_true_continue_pass_when_decide_then_promote() -> None:
    stats = nanogen6_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.5] * 10,
        gen_errors=[False] * 10,
        gen_peak_scores=[9.0] * 10,
        gen_bank_scores=[9.0] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
        n_bank_grounded=0,
        n_abstain=0,
        n_snippet_prefix=8,
        n_span_fallback=0,
        n_true_continue=10,
    )
    assert stats["pass_gen"] is True
    assert decide_nanogen6(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = nanogen6_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[9.0] * 10,
        gen_errors=[False] * 10,
        gen_peak_scores=[9.0] * 10,
        gen_bank_scores=[9.0] * 10,
        n_true_hit=9,
        n_false_hit=1,
        n_period=0,
        n_fix=0,
        n_peak=0,
        n_bank_grounded=0,
        n_abstain=0,
        n_true_continue=10,
    )
    assert decide_nanogen6(stats) == "KILL"


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_nanogen6_lookup(
        mode="WRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("NANOGEN6 LOOKUP" in n for n in notes)
