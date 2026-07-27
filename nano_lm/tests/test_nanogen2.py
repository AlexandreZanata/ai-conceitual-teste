"""Contract: Wave AR5 H-NANOGEN2 — ablated gen gate (pesquisa §5)."""

from __future__ import annotations

from nanogen2_ops import (
    MIN_GEN_MEAN,
    MIN_LOOKUP_MEAN,
    NANOGEN2_HYPOTHESIS,
    NANOGEN2_ID,
    NANOGEN2_N,
    NANOGEN2_PACK,
    NANOGEN2_THESIS,
    PARENT_NANOGEN_ABLATED,
    apply_bank_grounded_short,
    decide_nanogen2,
    gold_in_context,
    nanogen2_stats,
    score_nanogen2_gen,
    score_nanogen2_lookup,
)


def test_given_contract_when_constants_then_match_ar5_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AR5 — ablated≥5 PROMOTE else HOLD
    assert NANOGEN2_ID == "H-NANOGEN2"
    assert NANOGEN2_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_GEN_MEAN == 5.0
    assert PARENT_NANOGEN_ABLATED == 4.0
    assert len(NANOGEN2_PACK) == 10
    assert "ablated" in NANOGEN2_HYPOTHESIS.lower()
    assert "5.0" in NANOGEN2_HYPOTHESIS
    assert "ablated" in NANOGEN2_THESIS.lower()


def test_given_pack_when_kinds_then_held_and_para() -> None:
    kinds = [p["kind"] for p in NANOGEN2_PACK]
    assert kinds.count("held-out") == 5
    assert kinds.count("paraphrase") == 5


def test_given_gold_in_context_when_present_then_true() -> None:
    assert gold_in_context(gold="CS = ENT / 32", context="… CS = ENT / 32 …")
    assert not gold_in_context(gold="CS = ENT / 32", context="unrelated")


def test_given_junk_decode_when_bank_grounded_then_short_gold() -> None:
    text, used = apply_bank_grounded_short(
        decode_text="Once upon a time there was a little",
        context="BIP-39 checksum CS = ENT / 32 for ENT bits.",
        bank_gold="CS = ENT / 32",
    )
    assert used is True
    assert text == "CS = ENT / 32"


def test_given_bank_grounded_when_ablated_score_then_excluded() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": True,
    }
    score, err, notes = score_nanogen2_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("excluded" in n.lower() for n in notes)


def test_given_ablated_pass_when_decide_then_promote() -> None:
    stats = nanogen2_stats(
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
    )
    assert stats["pass_gen"] is True
    assert stats["beats_nanogen_ablated"] is True
    assert decide_nanogen2(stats) == "PROMOTE"


def test_given_ablated_low_when_decide_then_hold() -> None:
    stats = nanogen2_stats(
        lookup_scores=[9.0] * 10,
        lookup_errors=[False] * 10,
        gen_scores=[4.0] * 10,
        gen_errors=[True] * 10,
        gen_peak_scores=[9.0] * 10,
        gen_bank_scores=[9.0] * 10,
        n_true_hit=10,
        n_false_hit=0,
        n_period=0,
        n_fix=0,
        n_peak=10,
        n_bank_grounded=8,
        n_abstain=8,
    )
    assert stats["peak_only_lift"] is True
    assert stats["gen_bank_mean"] == 9.0
    assert decide_nanogen2(stats) == "HOLD"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = nanogen2_stats(
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
        n_peak=10,
        n_bank_grounded=0,
        n_abstain=0,
    )
    assert decide_nanogen2(stats) == "KILL"


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_nanogen2_lookup(
        mode="WRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("NANOGEN2 LOOKUP" in n for n in notes)
