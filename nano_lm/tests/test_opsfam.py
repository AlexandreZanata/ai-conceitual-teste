"""Contract: Wave BC1 H-OPSFAM — BC-FOREVER FH 0 via family gate · BA/BB/AZ hold."""

from __future__ import annotations

from bc_session_ops import BC0_FOREVER_ROWS
from opsfam_ops import (
    NOVEL_PROBES,
    OPSFAM_ANTI_FP,
    OPSFAM_CLAIM,
    OPSFAM_ID,
    OPSFAM_THESIS,
    bars_from_scoreboard,
    decide_opsfam,
    extract_opsfam_board,
    score_live_row,
)
from semwrap_ops import contrastive_reject, intent_ask_must_abstain


def _board(**overrides: object) -> dict:
    base = {
        "bc_forever_false_hit": 0,
        "bc_forever_ok_n": 18,
        "bc_forever_n": 18,
        "ba_forever_false_hit": 0,
        "ba_forever_ok_n": 15,
        "ba_forever_n": 15,
        "bb_forever_false_hit": 0,
        "bb_forever_ok_n": 15,
        "bb_forever_n": 15,
        "az_hold_false_hit": 0,
        "az_hold_ok_n": 12,
        "az_hold_n": 12,
        "overrefuse_miss": 0,
        "overrefuse_ok_n": 3,
        "overrefuse_n": 3,
        "live_ask_ok_fp_miss": "2/0/0+12",
        "live_scores": {"OK": 2, "FP": 0, "MISS": 0, "ABSTAIN-OK": 12},
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
        "ba_bb_pass_neq_bc_forever": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }
    base.update(overrides)
    return base


def test_given_bc_forever_traps_when_contrast_then_reject_family() -> None:
    # GIVEN/WHEN/THEN: BC1 forever gate — wrong gold must reject
    add_q = (
        "Write a short Python function named add that returns the sum "
        "of two integers a and b."
    )
    add_g = "def add(a, b):\n    return a + b"
    assert contrastive_reject(
        "Write a short Python function named floordiv that returns a // b.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a short Python function named neg1 that returns "
        "the negation of a.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a short Python function named gcd2 that returns "
        "the gcd of a and b.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a short Python function named lshift2 that returns "
        "a shifted left by b bits.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a short Python function named rshift2 that returns "
        "a shifted right by b bits.",
        add_q,
        add_g,
    )
    assert contrastive_reject(
        "Write a short Python function named nand2 that returns "
        "the bitwise nand of a and b.",
        add_q,
        add_g,
    )
    assert not contrastive_reject(
        "Remove all items from list `a` — one method call.",
        "Remove all items from list `a` — one method call.",
        "a.clear()",
    )


def test_given_bc_forever_ask_when_must_abstain_then_true() -> None:
    assert intent_ask_must_abstain(
        "Write a short Python function named floordiv that returns a // b."
    )
    assert intent_ask_must_abstain(
        "Implement floor_div_pair(a,b) returning integer // of a by b "
        "— not a+b."
    )
    assert intent_ask_must_abstain(
        "Bitwise NAND helper bit_nand(a,b) returning ~(a & b) — never a+b."
    )
    assert not intent_ask_must_abstain(
        "Remove all items from list `a` — one method call."
    )
    assert not intent_ask_must_abstain(
        "Write a short Python function named add that returns "
        "the sum of two integers a and b."
    )


def test_given_novel_probes_when_read_then_outside_forever_seeds() -> None:
    assert len(NOVEL_PROBES) >= 10
    forever_q = {str(p["question"]).strip() for p in BC0_FOREVER_ROWS}
    novel_q = {str(p["question"]).strip() for p in NOVEL_PROBES}
    assert forever_q.isdisjoint(novel_q)
    assert all(p["expect_mode"] == "ABSTAIN" for p in NOVEL_PROBES)
    assert all(intent_ask_must_abstain(str(p["question"])) for p in NOVEL_PROBES)


def test_given_bars_when_read_then_bc_ba_bb_az_zero() -> None:
    bars = bars_from_scoreboard()
    assert int(bars["bc_forever_false_hit_max"]) == 0
    assert int(bars["ba_forever_false_hit_max"]) == 0
    assert int(bars["bb_forever_false_hit_max"]) == 0
    assert int(bars["az_hold_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert bars["ba_bb_pass_neq_bc_forever"] is True
    assert bars["bank_stuff_forbidden"] is True
    assert int(bars["novel_probes_min"]) >= 10


def test_given_live_row_when_lookup_on_abstain_then_fp() -> None:
    assert score_live_row({"product_mode": "LOOKUP"}, expect_mode="ABSTAIN") == "FP"
    assert (
        score_live_row({"product_mode": "ABSTAIN"}, expect_mode="ABSTAIN")
        == "ABSTAIN-OK"
    )
    assert score_live_row(
        {"product_mode": "LOOKUP", "completion": "a.clear()"},
        expect_mode="LOOKUP",
    ) == "OK"


def test_given_board_when_decide_then_promote() -> None:
    out = decide_opsfam(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert OPSFAM_ID in out


def test_given_bc_fh_when_decide_then_kill() -> None:
    out = decide_opsfam(board=_board(bc_forever_false_hit=1), anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "bc_forever" in out


def test_given_bb_fh_when_decide_then_kill() -> None:
    out = decide_opsfam(board=_board(bb_forever_false_hit=1), anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "bb_forever" in out


def test_given_live_fp_when_decide_then_kill() -> None:
    out = decide_opsfam(board=_board(live_fp=1), anti_fp_signed=True)
    assert out.startswith("KILL")
    assert "live" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_opsfam(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_notes_when_read_then_anti_fp_and_claim() -> None:
    assert "floordiv" in OPSFAM_THESIS.lower() or "BC-FOREVER" in OPSFAM_THESIS
    assert OPSFAM_ID == "H-OPSFAM"
    assert "gibberish-tail" in OPSFAM_CLAIM
    assert "LOOKUP" in OPSFAM_ANTI_FP
    assert "NANOGEN13" in OPSFAM_ANTI_FP or "nanogen13" in OPSFAM_ANTI_FP.lower()


def test_given_extract_when_empty_packs_then_counts_zero() -> None:
    board = extract_opsfam_board(
        bc_rows=[],
        ba_rows=[],
        bb_rows=[],
        az_rows=[],
        overrefuse_rows=[],
        live_scores=["ABSTAIN-OK", "OK"],
        near={"product_mode": "ABSTAIN"},
        peak={"product_mode": "PEAK", "completion": "ownership"},
        known={"product_mode": "LOOKUP", "completion": "def add"},
        decode={"product_mode": "ABSTAIN", "abstained": True},
        metrics={"paths": {}, "kb": {"coverage_pct": 100.0, "holes": []}},
        ship={"arms": []},
    )
    assert board["bc_forever_false_hit"] == 0
    assert board["bb_forever_false_hit"] == 0
    assert board["live_fp"] == 0
    assert board["ba_bb_pass_neq_bc_forever"] is True
