"""Contract: Wave AU3 H-NANOGEN5 — STRICT ablated gen vs NANOGEN4 5.5."""

from __future__ import annotations

from nanogen5_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    NANOGEN5_HYPOTHESIS,
    NANOGEN5_ID,
    NANOGEN5_N,
    NANOGEN5_PACK,
    NANOGEN5_THESIS,
    PARENT_NANOGEN4_ABLATED,
    apply_gibberish_tail_gate,
    continuation_is_gibberish,
    decide_nanogen5,
    nanogen5_stats,
    score_nanogen5_gen,
    score_nanogen5_lookup,
    short_answer_token_f1,
)


def test_given_contract_when_constants_then_match_au3_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AU3 — strict_ablated≥5.5 PROMOTE else HOLD
    assert NANOGEN5_ID == "H-NANOGEN5"
    assert NANOGEN5_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.5
    assert PARENT_NANOGEN4_ABLATED == 5.5
    assert len(NANOGEN5_PACK) == 10
    hyp = NANOGEN5_HYPOTHESIS.lower()
    assert "ablated" in hyp
    assert "5.5" in NANOGEN5_HYPOTHESIS
    assert "strict" in hyp
    assert "gibberish" in hyp
    assert "f1" in hyp or "hitl" in hyp
    assert "gold-substring" in hyp or "gold substring" in hyp
    assert "ablated" in NANOGEN5_THESIS.lower()


def test_given_pack_when_kinds_then_held_and_para() -> None:
    kinds = [p["kind"] for p in NANOGEN5_PACK]
    assert kinds.count("held-out") == 5
    assert kinds.count("paraphrase") == 5


def test_given_exact_short_when_f1_then_high() -> None:
    assert short_answer_token_f1("CS = ENT / 32", "CS = ENT / 32") >= 0.90


def test_given_gibberish_tail_when_gate_then_truncate() -> None:
    # GIVEN snippet + TinyStories tail
    text = (
        "CS = ENT / 32 Once upon a time there was a little story "
        "looking for everything really quickly"
    )
    assert continuation_is_gibberish(text=text, prefix="CS = ENT / 32")
    out, trunc, refuse = apply_gibberish_tail_gate(
        text=text, prefix="CS = ENT / 32"
    )
    assert trunc is True and refuse is False
    assert out == "CS = ENT / 32"


def test_given_buried_gold_when_strict_score_then_fail() -> None:
    # GIVEN gold substring buried in junk without truncate flag
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": False,
        "snippet_prefix": True,
        "gibberish_tail": True,
        "gibberish_tail_truncated": False,
    }
    score, err, notes = score_nanogen5_gen(
        completion=(
            "CS = ENT / 32 Once upon a time there was a little "
            "story looking for everything"
        ),
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("gibberish" in n.lower() for n in notes)


def test_given_truncated_span_when_strict_score_then_pass() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": False,
        "snippet_prefix": True,
        "gibberish_tail_truncated": True,
    }
    score, err, notes = score_nanogen5_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score >= 5.5 and err is False
    assert any("strict" in n.lower() or "f1" in n.lower() for n in notes)


def test_given_bank_grounded_when_ablated_then_excluded() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": True,
    }
    score, err, notes = score_nanogen5_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("excluded" in n.lower() for n in notes)


def test_given_strict_pass_when_decide_then_promote() -> None:
    stats = nanogen5_stats(
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
        n_gibberish_truncated=6,
    )
    assert stats["pass_gen"] is True
    assert stats["beats_nanogen4_ablated"] is True
    assert stats["n_gibberish_truncated"] == 6
    assert decide_nanogen5(stats) == "PROMOTE"


def test_given_strict_low_when_decide_then_hold() -> None:
    stats = nanogen5_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[5.0] * 10,
        gen_errors=[True] * 10,
        gen_peak_scores=[9.0] * 10,
        gen_bank_scores=[9.0] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
        n_bank_grounded=0,
        n_abstain=0,
        n_snippet_prefix=3,
        n_gibberish_truncated=1,
    )
    assert stats["pass_gen"] is False
    assert decide_nanogen5(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = nanogen5_stats(
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
    )
    assert decide_nanogen5(stats) == "KILL"


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_nanogen5_lookup(
        mode="WRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("NANOGEN5 LOOKUP" in n for n in notes)
