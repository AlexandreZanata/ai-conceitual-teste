"""Contract: Wave AT3 H-NANOGEN4 — ablated gen gate vs NANOGEN3 4.3."""

from __future__ import annotations

from nanogen4_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    NANOGEN4_HYPOTHESIS,
    NANOGEN4_ID,
    NANOGEN4_N,
    NANOGEN4_PACK,
    NANOGEN4_THESIS,
    PARENT_NANOGEN3_ABLATED,
    apply_snippet_prefix_decode,
    decide_nanogen4,
    gold_in_context,
    nanogen4_stats,
    score_nanogen4_gen,
    score_nanogen4_lookup,
    select_snippet_span,
)


def test_given_contract_when_constants_then_match_at3_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AT3 — ablated≥5 PROMOTE else HOLD
    assert NANOGEN4_ID == "H-NANOGEN4"
    assert NANOGEN4_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert PARENT_NANOGEN3_ABLATED == 4.3
    assert len(NANOGEN4_PACK) == 10
    assert "ablated" in NANOGEN4_HYPOTHESIS.lower()
    assert "5.0" in NANOGEN4_HYPOTHESIS
    assert "4.3" in NANOGEN4_HYPOTHESIS
    hyp_l = NANOGEN4_HYPOTHESIS.lower()
    assert "snippet" in hyp_l or "prefix" in hyp_l
    assert "bank-gold" in hyp_l or "bank gold" in hyp_l
    assert "ablated" in NANOGEN4_THESIS.lower()


def test_given_pack_when_kinds_then_held_and_para() -> None:
    kinds = [p["kind"] for p in NANOGEN4_PACK]
    assert kinds.count("held-out") == 5
    assert kinds.count("paraphrase") == 5


def test_given_gold_in_context_when_present_then_true() -> None:
    assert gold_in_context(gold="CS = ENT / 32", context="… CS = ENT / 32 …")
    assert not gold_in_context(gold="CS = ENT / 32", context="unrelated")


def test_given_bank_grounded_when_ablated_score_then_excluded() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": True,
    }
    score, err, notes = score_nanogen4_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("excluded" in n.lower() for n in notes)
    assert any("NANOGEN4" in n for n in notes)


def test_given_peak_used_when_ablated_score_then_excluded() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": True,
        "bank_grounded": False,
    }
    score, err, notes = score_nanogen4_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("peak" in n.lower() for n in notes)


def test_given_snippet_prefix_when_ablated_then_counts() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": False,
        "snippet_prefix": True,
    }
    score, err, notes = score_nanogen4_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score >= 5.0 and err is False
    assert any("snippet-prefix" in n.lower() for n in notes)


def test_given_rag_context_when_snippet_prefix_then_seeds() -> None:
    text, used, prefix = apply_snippet_prefix_decode(
        decode_text="Once upon a time there was a little",
        question="What is the BIP-39 checksum length formula?",
        context="BIP-39 checksum CS = ENT / 32 for ENT bits of entropy.",
    )
    assert used is True
    assert "CS = ENT / 32" in text or "CS = ENT/32" in text.replace(" ", "")
    assert prefix
    span = select_snippet_span(
        question="What is the BIP-39 checksum length formula?",
        context="BIP-39 checksum CS = ENT / 32 for ENT bits of entropy.",
    )
    assert span is not None


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = nanogen4_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[9.0] * 10,
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
        n_snippet_prefix=6,
    )
    assert stats["pass_gen"] is True
    assert stats["beats_nanogen3_ablated"] is True
    assert stats["n_snippet_prefix"] == 6
    assert decide_nanogen4(stats) == "PROMOTE"


def test_given_ablated_low_when_decide_then_hold() -> None:
    stats = nanogen4_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.3] * 10,
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
    )
    assert stats["pass_gen"] is False
    assert stats["peak_only_lift"] is True
    assert decide_nanogen4(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = nanogen4_stats(
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
    assert decide_nanogen4(stats) == "KILL"


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_nanogen4_lookup(
        mode="WRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("NANOGEN4 LOOKUP" in n for n in notes)
