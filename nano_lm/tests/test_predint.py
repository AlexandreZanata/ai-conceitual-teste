"""Contract: Wave BF1 H-PREDINT — BF-FOREVER FH 0 via predicate gate · holds."""

from __future__ import annotations

from be_session_ops import BE0_FOREVER_ROWS
from bf_session_ops import BF0_FOREVER_ROWS
from predint_ops import (
    NOVEL_PROBES,
    PREDINT_ANTI_FP,
    PREDINT_CLAIM,
    PREDINT_ID,
    PREDINT_THESIS,
    bars_from_scoreboard,
    decide_predint,
    extract_predint_board,
    score_live_row,
)
from semwrap_ops import contrastive_reject, intent_ask_must_abstain


def _board(**overrides: object) -> dict:
    base = {
        "bf_forever_false_hit": 0,
        "bf_forever_ok_n": 12,
        "bf_forever_n": 12,
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
        "live_ask_ok_fp_miss": "2/0/0+16",
        "live_scores": {"OK": 2, "FP": 0, "MISS": 0, "ABSTAIN-OK": 16},
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
        "ba_bb_bc_bd_be_pass_neq_bf_forever": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }
    base.update(overrides)
    return base


def test_given_bf_predicate_traps_when_contrast_then_reject_family() -> None:
    # GIVEN/WHEN/THEN: BF1 forever gate — predicate/boolean ≠ add
    add_q = (
        "Write a short Python function named add that returns the sum "
        "of two integers a and b."
    )
    add_g = "def add(a, b):\n    return a + b"
    assert contrastive_reject(
        "Write a Python function that returns True if a is even.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a Python function that returns True if a is odd.",
        add_q,
        add_g,
    )
    assert intent_ask_must_abstain(
        "Write a Python function that returns True if a is even."
    )
    assert intent_ask_must_abstain(
        "Return a boolean indicating whether n is positive."
    )
    assert intent_ask_must_abstain(
        "Boolean check — does integer a have remainder 0 mod 2?"
    )
    assert not intent_ask_must_abstain(add_q)
    assert not intent_ask_must_abstain(
        "How do I append x to list a in one Python method call?"
    )


def test_given_forever_when_scan_then_all_abstain_detectors() -> None:
    assert len(BF0_FOREVER_ROWS) >= 12
    for row in BF0_FOREVER_ROWS:
        assert intent_ask_must_abstain(str(row["question"]))
    assert all(
        intent_ask_must_abstain(str(p["question"])) for p in BE0_FOREVER_ROWS
    )


def test_given_novel_when_scan_then_disjoint_and_min_ten() -> None:
    forever_q = {str(p["question"]).strip() for p in BF0_FOREVER_ROWS}
    forever_q |= {str(p["question"]).strip() for p in BE0_FOREVER_ROWS}
    novel_q = {str(p["question"]).strip() for p in NOVEL_PROBES}
    assert len(NOVEL_PROBES) >= 10
    assert forever_q.isdisjoint(novel_q)
    assert all(p["expect_mode"] == "ABSTAIN" for p in NOVEL_PROBES)
    assert all(intent_ask_must_abstain(str(p["question"])) for p in NOVEL_PROBES)


def test_given_score_live_when_lookup_on_abstain_then_fp() -> None:
    assert score_live_row({"product_mode": "LOOKUP"}, expect_mode="ABSTAIN") == "FP"
    assert (
        score_live_row({"product_mode": "ABSTAIN"}, expect_mode="ABSTAIN")
        == "ABSTAIN-OK"
    )
    assert score_live_row(
        {"product_mode": "LOOKUP", "completion": "a.clear()"},
        expect_mode="LOOKUP",
    ) in {"OK", "MISS"}


def test_given_ready_board_when_decide_then_promote() -> None:
    out = decide_predint(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert PREDINT_ID in out


def test_given_bf_fp_when_decide_then_kill() -> None:
    out = decide_predint(
        board=_board(bf_forever_false_hit=1), anti_fp_signed=True
    )
    assert out.startswith("KILL")


def test_given_live_fp_when_decide_then_kill() -> None:
    out = decide_predint(
        board=_board(
            live_fp=1,
            live_scores={"OK": 1, "FP": 1, "MISS": 0, "ABSTAIN-OK": 14},
        ),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_predint(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_notes_when_read_then_claim_and_thesis() -> None:
    assert "≤5M" in PREDINT_CLAIM or "AF" in PREDINT_CLAIM
    assert "predicate" in PREDINT_THESIS.lower() or "BF-FOREVER" in PREDINT_THESIS
    assert "LOOKUP" in PREDINT_ANTI_FP
    bars = bars_from_scoreboard()
    assert int(bars["bf_forever_false_hit_max"]) == 0
    assert int(bars["be_forever_false_hit_max"]) == 0


def test_given_extract_when_all_ok_then_board_keys() -> None:
    empty = {
        "product_mode": "ABSTAIN",
        "mode": "NO_ANSWER",
        "completion": "NO_ANSWER",
    }
    known = {
        "product_mode": "LOOKUP",
        "mode": "WRAP_LOOKUP",
        "completion": "def add(a, b): return a + b",
    }
    metrics = {
        "paths": {
            "LOOKUP": {"stats": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0}},
            "PEAK": {"stats": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.04}},
            "DECODE": {"stats": {"p50_wall_ms": 11.0, "p99_wall_ms": 13.0}},
            "ABSTAIN": {"stats": {"p50_wall_ms": 95.0, "p99_wall_ms": 119.0}},
        },
        "kb": {"snap": {"coverage_pct": 100.0, "holes": ["open-world"]}},
    }
    board = extract_predint_board(
        bf_rows=[empty] * 12,
        be_rows=[empty] * 12,
        bd_rows=[empty] * 12,
        ba_rows=[empty] * 15,
        bb_rows=[empty] * 15,
        bc_rows=[empty] * 18,
        az_rows=[empty] * 12,
        overrefuse_rows=[
            {
                "product_mode": "LOOKUP",
                "completion": "a.clear()",
                "gold": "a.clear()",
            }
        ]
        * 3,
        live_scores=["OK", "ABSTAIN-OK"] * 8,
        near=empty,
        peak={"product_mode": "PEAK", "completion": "ownership"},
        known=known,
        decode=empty,
        metrics=metrics,
        ship={"arms": []},
    )
    assert board["bf_forever_false_hit"] == 0
    assert board["be_forever_false_hit"] == 0
    assert board["live_fp"] == 0
    assert board["modes_n"] == 4
