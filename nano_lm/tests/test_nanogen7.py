"""Contract: Wave AW3 H-NANOGEN7 — TAC true continue; span ≠ gen IQ."""

from __future__ import annotations

from nanogen7_ops import (
    CODE_TEACHER_ID,
    MIN_LOOKUP_MEAN,
    MIN_TEACHER_TOPK_FRAC,
    MIN_TRUE_CONTINUE_MEAN,
    NANOGEN7_HYPOTHESIS,
    NANOGEN7_ID,
    NANOGEN7_N,
    NANOGEN7_PACK,
    NANOGEN7_THESIS,
    PARENT_NANOGEN6_TRUE_CONTINUE,
    apply_tac_continue,
    decide_nanogen7,
    nanogen7_stats,
    score_nanogen7_gen,
    score_nanogen7_lookup,
)


def test_given_contract_when_constants_then_match_aw3_gate() -> None:
    # GIVEN/WHEN/THEN: pesquisa §2 AW3 — TAC true_continue≥5.5 else HOLD
    assert NANOGEN7_ID == "H-NANOGEN7"
    assert NANOGEN7_N == 10
    assert MIN_LOOKUP_MEAN == 7.0
    assert MIN_TRUE_CONTINUE_MEAN == 5.5
    assert PARENT_NANOGEN6_TRUE_CONTINUE == 0.0
    assert MIN_TEACHER_TOPK_FRAC == 0.50
    assert len(NANOGEN7_PACK) == 10
    hyp = NANOGEN7_HYPOTHESIS.lower()
    assert "tac" in hyp or "teacher" in hyp
    assert "top-k" in hyp or "topk" in hyp
    assert "novel" in hyp
    assert "span" in hyp
    assert "nanogen6" in hyp
    assert "rename" in hyp or "refuse-or-continue" in hyp
    assert "TAC" in NANOGEN7_THESIS or "teacher" in NANOGEN7_THESIS.lower()
    assert CODE_TEACHER_ID.startswith("bigcode/")


def test_given_pack_when_kinds_then_held_and_para() -> None:
    kinds = [p["kind"] for p in NANOGEN7_PACK]
    assert kinds.count("held-out") == 5
    assert kinds.count("paraphrase") == 5


def test_given_span_only_when_tac_then_span_fallback() -> None:
    out, kind, trunc, refuse, tok = apply_tac_continue(
        text="CS = ENT / 32",
        prefix="CS = ENT / 32",
        teacher_topk_frac=1.0,
    )
    assert kind == "span_fallback"
    assert trunc is True and refuse is False and tok is False
    assert out == "CS = ENT / 32"


def test_given_novel_when_teacher_fail_then_abstain() -> None:
    out, kind, trunc, refuse, tok = apply_tac_continue(
        text=(
            "CS = ENT / 32 Checksum equals ENT divided by 32 for "
            "BIP-39 mnemonics."
        ),
        prefix="CS = ENT / 32",
        teacher_topk_frac=0.1,
    )
    assert kind == "abstain"
    assert refuse is True and tok is False


def test_given_novel_when_teacher_pass_then_true_continue() -> None:
    out, kind, trunc, refuse, tok = apply_tac_continue(
        text=(
            "CS = ENT / 32 Checksum equals ENT divided by 32 for "
            "BIP-39 mnemonics."
        ),
        prefix="CS = ENT / 32",
        teacher_topk_frac=0.9,
    )
    assert kind == "true_continue"
    assert refuse is False and tok is True
    assert "Checksum" in out or "BIP" in out


def test_given_missing_teacher_when_tac_then_abstain() -> None:
    _out, kind, _t, refuse, tok = apply_tac_continue(
        text=(
            "CS = ENT / 32 Checksum equals ENT divided by 32 for "
            "BIP-39 mnemonics."
        ),
        prefix="CS = ENT / 32",
        teacher_topk_frac=None,
    )
    assert kind == "abstain"
    assert refuse is True and tok is False


def test_given_span_fallback_when_score_then_zero_gen_credit() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 10.0,
        "n_new": 8,
        "peak_used": False,
        "bank_grounded": False,
        "snippet_prefix": True,
        "continue_kind": "span_fallback",
        "span_fallback": True,
        "teacher_topk_ok": False,
        "product_mode": "PEAK",
    }
    score, err, notes = score_nanogen7_gen(
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("span-fallback" in n.lower() or "≠ gen" in n for n in notes)


def test_given_true_continue_teacher_when_f1_high_then_pass() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 12.0,
        "n_new": 16,
        "peak_used": False,
        "bank_grounded": False,
        "snippet_prefix": True,
        "continue_kind": "true_continue",
        "span_fallback": False,
        "teacher_topk_ok": True,
        "teacher_topk_frac": 0.85,
        "product_mode": "DECODE",
    }
    score, err, notes = score_nanogen7_gen(
        completion=(
            "CS = ENT / 32 is the BIP-39 checksum relation for "
            "mnemonic entropy length."
        ),
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score >= 5.5 and err is False
    assert any("tac" in n.lower() or "teacher" in n.lower() for n in notes)


def test_given_true_continue_without_teacher_when_score_then_fail() -> None:
    payload = {
        "mode": "QPFB2+BEAMKV+GROUNDED+ANTI_PERIOD+ABLATED",
        "wall_ms": 12.0,
        "n_new": 16,
        "continue_kind": "true_continue",
        "span_fallback": False,
        "teacher_topk_ok": False,
        "product_mode": "DECODE",
    }
    score, err, notes = score_nanogen7_gen(
        completion=(
            "CS = ENT / 32 is the BIP-39 checksum relation for "
            "mnemonic entropy length."
        ),
        expected_gold="CS = ENT / 32",
        payload=payload,
        peak_ablated=True,
    )
    assert score == 4.0 and err is True
    assert any("teacher" in n.lower() for n in notes)


def test_given_only_span_fallback_when_stats_then_hold() -> None:
    stats = nanogen7_stats(
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
        n_bank_grounded=0,
        n_abstain=7,
        n_snippet_prefix=10,
        n_span_fallback=3,
        n_true_continue=0,
        n_teacher_topk_pass=0,
    )
    assert stats["pass_gen"] is False
    assert stats["nanogen6_refuse_or_continue_archived"] is True
    assert decide_nanogen7(stats) == "HOLD"


def test_given_true_continue_pass_when_decide_then_promote() -> None:
    stats = nanogen7_stats(
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
        n_teacher_topk_pass=10,
    )
    assert stats["pass_gen"] is True
    assert decide_nanogen7(stats) == "PROMOTE"


def test_given_false_hit_when_decide_then_kill() -> None:
    stats = nanogen7_stats(
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
        n_teacher_topk_pass=10,
    )
    assert decide_nanogen7(stats) == "KILL"


def test_given_lookup_true_hit_when_score_then_ok() -> None:
    payload = {"mode": "WRAP_LOOKUP", "wall_ms": 0.0, "n_new": 0}
    score, err, notes = score_nanogen7_lookup(
        mode="WRAP_LOOKUP",
        completion="CS = ENT / 32",
        expected_gold="CS = ENT / 32",
        lookup_kind="TRUE_HIT",
        payload=payload,
    )
    assert score >= 8.0 and err is False
    assert any("NANOGEN7 LOOKUP" in n for n in notes)
