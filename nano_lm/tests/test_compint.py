"""Contract: Wave BE1 H-COMPINT — BE-FOREVER FH 0 via type/schema gate · holds."""

from __future__ import annotations

from be_session_ops import BE0_FOREVER_ROWS
from bd_session_ops import BD0_FOREVER_ROWS
from compint_ops import (
    COMPINT_ANTI_FP,
    COMPINT_CLAIM,
    COMPINT_ID,
    COMPINT_THESIS,
    NOVEL_PROBES,
    bars_from_scoreboard,
    decide_compint,
    extract_compint_board,
    score_live_row,
)
from semwrap_ops import contrastive_reject, intent_ask_must_abstain


def _board(**overrides: object) -> dict:
    base = {
        "be_forever_false_hit": 0,
        "be_forever_ok_n": 12,
        "be_forever_n": 12,
        "bd_forever_false_hit": 0,
        "bd_forever_ok_n": 12,
        "bd_forever_n": 12,
        "ba_forever_false_hit": 0,
        "ba_forever_ok_n": 15,
        "ba_forever_n": 15,
        "bb_forever_false_hit": 0,
        "bb_forever_ok_n": 15,
        "bb_forever_n": 15,
        "bc_forever_false_hit": 0,
        "bc_forever_ok_n": 18,
        "bc_forever_n": 18,
        "az_hold_false_hit": 0,
        "az_hold_ok_n": 12,
        "az_hold_n": 12,
        "overrefuse_miss": 0,
        "overrefuse_ok_n": 3,
        "overrefuse_n": 3,
        "live_ask_ok_fp_miss": "2/0/0+15",
        "live_scores": {"OK": 2, "FP": 0, "MISS": 0, "ABSTAIN-OK": 15},
        "live_fp": 0,
        "false_hit": 0,
        "near_miss_ok": True,
        "near_miss_mode": "ABSTAIN",
        "peak_ok": True,
        "peak_mode": "PEAK",
        "known_lookup_ok": True,
        "decode_content_ok": True,
        "decode_mode": "ABSTAIN",
        "decode_abstained": True,
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0},
            "PEAK": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.04},
            "DECODE": {"p50_wall_ms": 11.0, "p99_wall_ms": 13.0},
            "ABSTAIN": {"p50_wall_ms": 95.0, "p99_wall_ms": 119.0},
        },
        "kb_coverage_pct": 100.0,
        "kb_hole_list": ["open-world"],
        "modes_visible": ["ABSTAIN", "DECODE", "LOOKUP", "PEAK"],
        "modes_n": 4,
        "pack_pass_neq_forever": True,
        "ba_bb_bc_bd_pass_neq_be_forever": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }
    base.update(overrides)
    return base


def test_given_be_type_traps_when_contrast_then_reject_family() -> None:
    # GIVEN/WHEN/THEN: BE1 forever gate — type/coercion ≠ add
    add_q = (
        "Write a short Python function named add that returns the sum "
        "of two integers a and b."
    )
    add_g = "def add(a, b):\n    return a + b"
    assert contrastive_reject(
        "How do I convert string s to integer in Python?",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Convert string s to an int in Python — one expression.",
        add_q,
        add_g,
    )
    assert intent_ask_must_abstain(
        "How do I convert string s to integer in Python?"
    )
    assert intent_ask_must_abstain(
        "How do I convert integer n to a string in Python?"
    )
    assert intent_ask_must_abstain(
        "How do I check if string s is numeric in Python?"
    )
    assert not intent_ask_must_abstain(add_q)
    assert not intent_ask_must_abstain(
        "How do I append x to list a in one Python method call?"
    )


def test_given_forever_when_scan_then_all_abstain_detectors() -> None:
    assert len(BE0_FOREVER_ROWS) >= 12
    for row in BE0_FOREVER_ROWS:
        assert intent_ask_must_abstain(str(row["question"]))
    assert all(intent_ask_must_abstain(str(p["question"])) for p in BD0_FOREVER_ROWS)


def test_given_novel_when_scan_then_disjoint_and_min_ten() -> None:
    forever_q = {str(p["question"]).strip() for p in BE0_FOREVER_ROWS}
    forever_q |= {str(p["question"]).strip() for p in BD0_FOREVER_ROWS}
    novel_q = {str(p["question"]).strip() for p in NOVEL_PROBES}
    assert len(NOVEL_PROBES) >= 10
    assert forever_q.isdisjoint(novel_q)
    assert all(p["expect_mode"] == "ABSTAIN" for p in NOVEL_PROBES)
    assert all(intent_ask_must_abstain(str(p["question"])) for p in NOVEL_PROBES)


def test_given_board_when_decide_then_promote() -> None:
    out = decide_compint(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert COMPINT_ID in out


def test_given_be_fp_when_decide_then_kill() -> None:
    out = decide_compint(board=_board(be_forever_false_hit=1), anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "be_forever" in out


def test_given_bd_hold_fp_when_decide_then_kill() -> None:
    out = decide_compint(board=_board(bd_forever_false_hit=1), anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "bd_forever" in out


def test_given_live_fp_when_decide_then_kill() -> None:
    out = decide_compint(
        board=_board(
            live_fp=1,
            live_scores={"OK": 1, "FP": 1, "MISS": 0, "ABSTAIN-OK": 10},
        ),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "live ask FP" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_compint(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_notes_when_read_then_anti_fp_charter() -> None:
    assert "LOOKUP" in COMPINT_ANTI_FP
    assert "type" in COMPINT_ANTI_FP.lower() or "BE-FOREVER" in COMPINT_ANTI_FP
    assert "gibberish-tail" in COMPINT_CLAIM
    assert "type" in COMPINT_THESIS.lower() or "BE-FOREVER" in COMPINT_THESIS
    bars = bars_from_scoreboard()
    assert int(bars.get("be_forever_false_hit_max", 1)) == 0
    assert bars.get("ba_bb_bc_bd_pass_neq_be_forever") is True


def test_given_live_row_when_score_then_fp_on_lookup_abstain_expect() -> None:
    assert score_live_row({"product_mode": "LOOKUP"}, expect_mode="ABSTAIN") == "FP"
    assert (
        score_live_row({"product_mode": "ABSTAIN"}, expect_mode="ABSTAIN")
        == "ABSTAIN-OK"
    )


def test_given_extract_when_pack_ok_then_be_fh_zero() -> None:
    abstain = {"product_mode": "ABSTAIN", "mode": "NO_ANSWER", "abstained": True}
    lookup = {
        "product_mode": "LOOKUP",
        "mode": "WRAP_LOOKUP",
        "completion": "a.clear()",
    }
    board = extract_compint_board(
        be_rows=[abstain] * 12,
        bd_rows=[abstain] * 12,
        ba_rows=[abstain] * 15,
        bb_rows=[abstain] * 15,
        bc_rows=[abstain] * 18,
        az_rows=[abstain] * 12,
        overrefuse_rows=[lookup] * 3,
        live_scores=["OK", "ABSTAIN-OK"] * 6,
        near=abstain,
        peak={"product_mode": "PEAK", "completion": "ownership"},
        known={
            "product_mode": "LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        },
        decode=abstain,
        metrics={
            "paths": {
                "LOOKUP": {"stats": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0}},
                "PEAK": {"stats": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.04}},
                "DECODE": {"stats": {"p50_wall_ms": 11.0, "p99_wall_ms": 13.0}},
                "ABSTAIN": {"stats": {"p50_wall_ms": 90.0, "p99_wall_ms": 120.0}},
            },
            "kb": {"snap": {"coverage_pct": 100.0, "holes": ["open-world"]}},
        },
        ship={"arms": []},
    )
    assert board["be_forever_false_hit"] == 0
    assert board["bd_forever_false_hit"] == 0
    assert board["live_fp"] == 0
