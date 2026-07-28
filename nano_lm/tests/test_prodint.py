"""Contract: Wave AY1 H-PRODINT — intent FH 0 Caminho A (pesquisa §5)."""

from __future__ import annotations

from ay_session_ops import AY0_MODES, AY0_PRODUCT_INT_CHARTER
from prodint_ops import (
    HARD_NATURAL_ROWS,
    INTENT_FP_ROWS,
    PRODINT_CLAIM,
    PRODINT_ID,
    PRODINT_THESIS,
    bars_from_int_charter,
    decide_prodint,
    extract_prodint_board,
    intent_false_hit,
    intent_row_ok,
)
from semwrap_ops import contrastive_reject, intent_ask_must_abstain


def _board(**over: object) -> dict:
    base = {
        "intent_false_hit": 0,
        "intent_ok_n": 12,
        "intent_n": 12,
        "intent_abstain_rate": 1.0,
        "hard_natural_para_hit": 1.0,
        "para_n_true": 18,
        "para_n": 18,
        "false_hit": 0,
        "near_miss_ok": True,
        "near_miss_mode": "ABSTAIN",
        "peak_ok": True,
        "peak_mode": "PEAK",
        "peak_completion": "Ownership is a set of rules that govern memory.",
        "known_lookup_ok": True,
        "decode_content_ok": True,
        "decode_mode": "ABSTAIN",
        "decode_completion": "NO_ANSWER",
        "decode_abstained": True,
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0},
            "PEAK": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.03},
            "DECODE": {"p50_wall_ms": 10.0, "p99_wall_ms": 12.0},
            "ABSTAIN": {"p50_wall_ms": 90.0, "p99_wall_ms": 110.0},
        },
        "kb_coverage_pct": 100.0,
        "kb_hole_list": ["example-hole"],
        "modes_visible": sorted(AY0_MODES),
        "modes_n": 4,
        "pack_fh_neq_live_intent": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }
    base.update(over)
    return base


def test_given_contract_when_constants_then_match_ay1() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AY1 — close intent FH debt
    assert PRODINT_ID == "H-PRODINT"
    assert "intent" in PRODINT_THESIS.lower()
    assert "gibberish-tail" in PRODINT_CLAIM
    assert len(INTENT_FP_ROWS) >= 12
    assert len(HARD_NATURAL_ROWS) >= 15
    bars = bars_from_int_charter(AY0_PRODUCT_INT_CHARTER)
    assert int(bars["intent_false_hit_max"]) == 0
    assert float(bars["hard_natural_para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert bars["default_ask_intent_mismatch"] == "ABSTAIN"
    assert bars["bank_stuff_forbidden"] is True
    assert bars["pack_fh_neq_live_intent"] is True
    assert bars["regression_hold"] is True


def test_given_intent_lookup_when_score_then_false_hit() -> None:
    assert intent_false_hit(
        {
            "product_mode": "LOOKUP",
            "mode": "SEMWRAP_LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        }
    )
    assert intent_row_ok(
        {"product_mode": "ABSTAIN", "mode": "NO_ANSWER", "completion": "NO_ANSWER"}
    )
    assert not intent_row_ok(
        {"product_mode": "LOOKUP", "mode": "SEMWRAP_LOOKUP", "completion": "def add"}
    )


def test_given_intent_traps_when_contrast_then_reject_mul_diff_clear_bip() -> None:
    # GIVEN/WHEN/THEN: AY1 intent gate — wrong gold must reject (no bank stuff)
    assert contrastive_reject(
        "Write a short Python function named mul that returns the product "
        "of two integers a and b.",
        "Write a short Python function named add that returns the sum "
        "of two integers a and b.",
        "def add(a, b):\n    return a + b",
    )
    assert contrastive_reject(
        "Write a Python function named add that returns the difference "
        "of two integers a and b.",
        "Write a short Python function named add that returns the sum "
        "of two integers a and b.",
        "def add(a, b):\n    return a + b",
    )
    assert contrastive_reject(
        "How do I remove a single element x from a Python list without "
        "clearing the whole list?",
        "Remove all items from list `a` — one method call.",
        "a.clear()",
    )
    assert contrastive_reject(
        "What is the BIP-39 wordlist length?",
        "BIP-39: what is the formula for checksum length CS in terms of ENT?",
        "CS = ENT / 32",
    )
    assert not contrastive_reject(
        "I need a Python helper that adds two numbers called a and b — "
        "name it add please",
        "Write a short Python function named add that returns the sum "
        "of two integers a and b.",
        "def add(a, b):\n    return a + b",
    )


def test_given_intent_ask_when_must_abstain_then_true_for_pack() -> None:
    assert intent_ask_must_abstain(
        "Write a short Python function named mul that returns the product "
        "of two integers a and b."
    )
    assert intent_ask_must_abstain("What is the BIP-39 wordlist length?")
    assert not intent_ask_must_abstain(
        "I need a Python helper that adds two numbers called a and b — "
        "name it add please"
    )


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_prodint(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert PRODINT_ID in out


def test_given_intent_fh_when_decide_then_kill() -> None:
    out = decide_prodint(
        board=_board(intent_false_hit=1, intent_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "intent" in out.lower()


def test_given_partial_abstain_when_decide_then_hold() -> None:
    out = decide_prodint(
        board=_board(intent_false_hit=0, intent_ok_n=10, intent_n=12),
        anti_fp_signed=True,
    )
    assert out.startswith("HOLD")
    assert "intent" in out.lower() or "abstain" in out.lower()


def test_given_low_para_when_decide_then_hold() -> None:
    out = decide_prodint(
        board=_board(hard_natural_para_hit=0.5, para_n_true=9, para_n=18),
        anti_fp_signed=True,
    )
    assert out.startswith("HOLD")
    assert "hard_natural" in out.lower() or "para" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_prodint(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_rows_when_extract_then_intent_fh_zero() -> None:
    intent = [
        {"id": f"AY-IFP-{i:02d}", "product_mode": "ABSTAIN", "mode": "NO_ANSWER"}
        for i in range(1, 13)
    ]
    board = extract_prodint_board(
        intent_rows=intent,
        para_hits=[True] * 18,
        near={"product_mode": "ABSTAIN", "mode": "NO_ANSWER", "completion": "NO_ANSWER"},
        peak={
            "product_mode": "PEAK",
            "completion": "Ownership rules govern memory.",
        },
        known={
            "product_mode": "LOOKUP",
            "mode": "WRAP_LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        },
        decode={
            "product_mode": "ABSTAIN",
            "mode": "NO_ANSWER",
            "completion": "NO_ANSWER",
            "abstained": True,
        },
        metrics={
            "paths": {
                "LOOKUP": {"stats": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0}},
                "PEAK": {"stats": {"p50_wall_ms": 1.0, "p99_wall_ms": 2.0}},
                "DECODE": {"stats": {"p50_wall_ms": 10.0, "p99_wall_ms": 12.0}},
                "ABSTAIN": {"stats": {"p50_wall_ms": 20.0, "p99_wall_ms": 30.0}},
            },
            "kb": {"snap": {"coverage_pct": 100.0, "holes": ["hole"]}},
        },
        ship={"arms": []},
    )
    assert board["intent_false_hit"] == 0
    assert board["intent_ok_n"] == 12
    assert board["hard_natural_para_hit"] == 1.0
    assert board["modes_n"] == 4
