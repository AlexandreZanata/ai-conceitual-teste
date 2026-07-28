"""Contract: Wave BD1 H-SEMINT — BD-FOREVER FH 0 via semantic gate · holds."""

from __future__ import annotations

from bd_session_ops import BD0_FOREVER_ROWS
from semint_ops import (
    NOVEL_PROBES,
    SEMINT_ANTI_FP,
    SEMINT_CLAIM,
    SEMINT_ID,
    SEMINT_THESIS,
    bars_from_scoreboard,
    decide_semint,
    extract_semint_board,
    score_live_row,
)
from semwrap_ops import contrastive_reject, intent_ask_must_abstain


def _board(**overrides: object) -> dict:
    base = {
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
        "live_ask_ok_fp_miss": "2/0/0+14",
        "live_scores": {"OK": 2, "FP": 0, "MISS": 0, "ABSTAIN-OK": 14},
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
        "ba_bb_bc_pass_neq_bd_forever": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }
    base.update(overrides)
    return base


def test_given_bd_forever_traps_when_contrast_then_reject_family() -> None:
    # GIVEN/WHEN/THEN: BD1 forever gate — wrong gold must reject
    add_q = (
        "Write a short Python function named add that returns the sum "
        "of two integers a and b."
    )
    add_g = "def add(a, b):\n    return a + b"
    fstr_g = "Begin the string with f or F before the opening quotation mark."
    assert contrastive_reject(
        "How do I reverse a string in Python?",
        "f-string FAQ",
        fstr_g,
    )
    assert contrastive_reject(
        "Write a Python function that multiplies a and b and returns "
        "the product.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Please write multiply(a, b) returning a times b.",
        add_q,
        add_g,
    )
    assert intent_ask_must_abstain("How do I reverse a string in Python?")
    assert intent_ask_must_abstain(
        "Write a Python function that multiplies a and b and returns "
        "the product."
    )
    assert intent_ask_must_abstain("Clamp x between lo and hi in Python.")
    assert not intent_ask_must_abstain(add_q)
    assert not intent_ask_must_abstain(
        "How do I append x to list a in one Python method call?"
    )


def test_given_forever_when_scan_then_all_abstain_detectors() -> None:
    assert len(BD0_FOREVER_ROWS) >= 12
    for row in BD0_FOREVER_ROWS:
        assert intent_ask_must_abstain(str(row["question"]))


def test_given_novel_when_scan_then_disjoint_and_min_ten() -> None:
    forever_q = {str(p["question"]).strip() for p in BD0_FOREVER_ROWS}
    novel_q = {str(p["question"]).strip() for p in NOVEL_PROBES}
    assert len(NOVEL_PROBES) >= 10
    assert forever_q.isdisjoint(novel_q)
    assert all(p["expect_mode"] == "ABSTAIN" for p in NOVEL_PROBES)


def test_given_board_when_decide_then_promote() -> None:
    out = decide_semint(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert SEMINT_ID in out


def test_given_bd_fp_when_decide_then_kill() -> None:
    out = decide_semint(board=_board(bd_forever_false_hit=1), anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "bd_forever" in out


def test_given_live_fp_when_decide_then_kill() -> None:
    out = decide_semint(
        board=_board(live_fp=1, live_scores={"OK": 1, "FP": 1, "MISS": 0, "ABSTAIN-OK": 10}),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "live ask FP" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_semint(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_notes_when_read_then_anti_fp_charter() -> None:
    assert "LOOKUP" in SEMINT_ANTI_FP
    assert "reverse" in SEMINT_ANTI_FP.lower() or "BD-FOREVER" in SEMINT_ANTI_FP
    assert "gibberish-tail" in SEMINT_CLAIM
    assert "SEMWRAP" in SEMINT_THESIS or "semantic" in SEMINT_THESIS.lower()
    bars = bars_from_scoreboard()
    assert int(bars["bd_forever_false_hit_max"]) == 0
    assert int(bars["bd_forever_min_n"]) >= 12


def test_given_live_row_when_score_then_fp_on_wrong_lookup() -> None:
    assert (
        score_live_row({"product_mode": "LOOKUP"}, expect_mode="ABSTAIN") == "FP"
    )
    assert (
        score_live_row({"product_mode": "ABSTAIN"}, expect_mode="ABSTAIN")
        == "ABSTAIN-OK"
    )


def test_given_empty_packs_when_extract_then_zeros() -> None:
    board = extract_semint_board(
        bd_rows=[],
        ba_rows=[],
        bb_rows=[],
        bc_rows=[],
        az_rows=[],
        overrefuse_rows=[],
        live_scores=["ABSTAIN-OK"] * 10,
        near={"product_mode": "ABSTAIN"},
        peak={"product_mode": "PEAK", "completion": "ownership"},
        known={"product_mode": "LOOKUP", "completion": "def add"},
        decode={"product_mode": "ABSTAIN", "abstained": True, "completion": "NO_ANSWER"},
        metrics={
            "paths": {
                "LOOKUP": {"stats": {"p50_wall_ms": 0, "p99_wall_ms": 0}},
                "PEAK": {"stats": {"p50_wall_ms": 0.01, "p99_wall_ms": 0.02}},
                "DECODE": {"stats": {"p50_wall_ms": 10, "p99_wall_ms": 12}},
                "ABSTAIN": {"stats": {"p50_wall_ms": 90, "p99_wall_ms": 110}},
            },
            "kb": {"snap": {"coverage_pct": 100.0, "holes": ["open-world"]}},
        },
        ship={"arms": []},
    )
    assert board["bd_forever_false_hit"] == 0
    assert board["live_fp"] == 0
    assert board["bank_stuff_forbidden"] is True
