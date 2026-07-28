"""Contract: Wave BA1 H-REALGAIN — forever FH 0 via gate · AZ hold."""

from __future__ import annotations

from ba_session_ops import BA0_FOREVER_ROWS
from realgain_ops import (
    REALGAIN_ANTI_FP,
    REALGAIN_CLAIM,
    REALGAIN_ID,
    REALGAIN_THESIS,
    bars_from_scoreboard,
    decide_realgain,
    extract_realgain_board,
    score_live_row,
)
from semwrap_ops import contrastive_reject, intent_ask_must_abstain


def _board(**overrides: object) -> dict:
    base = {
        "forever_false_hit": 0,
        "forever_ok_n": 15,
        "forever_n": 15,
        "az_hold_false_hit": 0,
        "az_hold_ok_n": 12,
        "az_hold_n": 12,
        "overrefuse_miss": 0,
        "overrefuse_ok_n": 3,
        "overrefuse_n": 3,
        "live_ask_ok_fp_miss": "2/0/0+3",
        "live_scores": {"OK": 2, "FP": 0, "MISS": 0, "ABSTAIN-OK": 3},
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
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }
    base.update(overrides)
    return base


def test_given_forever_traps_when_contrast_then_reject_pow_mod_max_sort() -> None:
    # GIVEN/WHEN/THEN: BA1 forever gate — wrong gold must reject
    add_q = (
        "Write a short Python function named add that returns the sum "
        "of two integers a and b."
    )
    add_g = "def add(a, b):\n    return a + b"
    assert contrastive_reject(
        "Write a short Python function named pow2 that returns "
        "a raised to the power of b for two integers.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a short Python function named mod that returns "
        "the remainder of a divided by b.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a short Python function named max2 that returns "
        "the larger of two integers a and b.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Sort list `a` ascending in place — one method call. "
        "Do not reverse it.",
        "Reverse list `a` in place — one method call.",
        "a.reverse()",
    )
    assert contrastive_reject(
        "What is the length of Python list a — one builtin call?",
        "How do I make a list of ten ints?",
        "range(10)]",
    )
    assert not contrastive_reject(
        "Remove all items from list `a` — one method call.",
        "Remove all items from list `a` — one method call.",
        "a.clear()",
    )


def test_given_forever_ask_when_must_abstain_then_true() -> None:
    assert intent_ask_must_abstain(
        "Write a short Python function named pow2 that returns "
        "a raised to the power of b for two integers."
    )
    assert intent_ask_must_abstain(
        "Sort list `a` ascending in place — one method call. "
        "Do not reverse it."
    )
    assert intent_ask_must_abstain(
        "What is the length of Python list a — one builtin call?"
    )
    assert not intent_ask_must_abstain(
        "Remove all items from list `a` — one method call."
    )
    assert not intent_ask_must_abstain(
        "Write a short Python function named add that returns "
        "the sum of two integers a and b."
    )


def test_given_forever_pack_when_read_then_min_fifteen() -> None:
    assert len(BA0_FOREVER_ROWS) >= 15
    classes = {r["class"] for r in BA0_FOREVER_ROWS}
    assert {"ops_pow", "ops_mod", "ops_max", "list_sort", "list_len"} <= classes


def test_given_score_labels_when_live_then_ok_fp_miss_abstain() -> None:
    assert (
        score_live_row({"product_mode": "LOOKUP", "completion": "def add"}, expect_mode="ABSTAIN")
        == "FP"
    )
    assert (
        score_live_row({"product_mode": "ABSTAIN"}, expect_mode="ABSTAIN")
        == "ABSTAIN-OK"
    )
    assert (
        score_live_row(
            {"product_mode": "LOOKUP", "completion": "a.clear()", "gold": "a.clear()"},
            expect_mode="LOOKUP",
        )
        == "OK"
    )
    assert (
        score_live_row({"product_mode": "ABSTAIN"}, expect_mode="LOOKUP") == "MISS"
    )


def test_given_bars_when_read_then_forever_zero() -> None:
    bars = bars_from_scoreboard()
    assert int(bars["forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert bars["bank_stuff_forbidden"] is True
    assert "REALGAIN" in REALGAIN_ID or REALGAIN_ID == "H-REALGAIN"
    assert "forever" in REALGAIN_THESIS.lower()
    assert "gibberish-tail" in REALGAIN_CLAIM
    assert "LOOKUP" in REALGAIN_ANTI_FP


def test_given_board_when_extract_then_counts() -> None:
    forever = [
        {"product_mode": "ABSTAIN", "mode": "NO_ANSWER"} for _ in range(15)
    ]
    az = [{"product_mode": "ABSTAIN", "mode": "NO_ANSWER"} for _ in range(12)]
    orf = [
        {
            "product_mode": "LOOKUP",
            "mode": "WRAP_LOOKUP",
            "completion": "a.clear()",
        }
        for _ in range(3)
    ]
    board = extract_realgain_board(
        forever_rows=forever,
        az_rows=az,
        overrefuse_rows=orf,
        live_scores=["ABSTAIN-OK", "OK", "FP"],
        near={"product_mode": "ABSTAIN"},
        peak={"product_mode": "PEAK", "completion": "ownership"},
        known={"product_mode": "LOOKUP", "completion": "def add"},
        decode={"product_mode": "ABSTAIN", "abstained": True, "completion": "NO_ANSWER"},
        metrics={
            "paths": {
                "LOOKUP": {"stats": {"p50_wall_ms": 0, "p99_wall_ms": 0}},
                "PEAK": {"stats": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.04}},
                "DECODE": {"stats": {"p50_wall_ms": 11, "p99_wall_ms": 13}},
                "ABSTAIN": {"stats": {"p50_wall_ms": 95, "p99_wall_ms": 119}},
            },
            "kb": {"snap": {"coverage_pct": 100.0, "holes": ["x"]}},
        },
        ship={"arms": []},
    )
    assert board["forever_false_hit"] == 0
    assert board["forever_ok_n"] == 15
    assert board["az_hold_false_hit"] == 0
    assert board["overrefuse_miss"] == 0
    assert board["live_fp"] == 1
    assert board["modes_n"] == 4


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_realgain(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert REALGAIN_ID in out


def test_given_forever_fh_when_decide_then_kill() -> None:
    out = decide_realgain(
        board=_board(forever_false_hit=1, forever_ok_n=14),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "forever" in out.lower()


def test_given_az_hold_fh_when_decide_then_kill() -> None:
    out = decide_realgain(
        board=_board(az_hold_false_hit=1, az_hold_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "az_hold" in out.lower()


def test_given_live_fp_when_decide_then_kill() -> None:
    out = decide_realgain(board=_board(live_fp=1), anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "live" in out.lower() or "FP" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_realgain(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out
