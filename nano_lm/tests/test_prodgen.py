"""Contract: Wave AZ1 H-PRODGEN — held-out FH 0 + no over-refuse (pesquisa §5)."""

from __future__ import annotations

from az_session_ops import AZ0_MODES, AZ0_PRODUCT_GEN_CHARTER
from prodgen_ops import (
    HARD_NATURAL_ROWS,
    HELDOUT_FP_ROWS,
    NAMED_INTENT_ROWS,
    OVERREFUSE_ROWS,
    PRODGEN_CLAIM,
    PRODGEN_ID,
    PRODGEN_THESIS,
    bars_from_gen_charter,
    decide_prodgen,
    extract_prodgen_board,
    intent_false_hit,
    overrefuse_miss,
    overrefuse_row_ok,
)
from semwrap_ops import contrastive_reject, intent_ask_must_abstain


def _board(**over: object) -> dict:
    base = {
        "heldout_false_hit": 0,
        "heldout_ok_n": 12,
        "heldout_n": 12,
        "heldout_abstain_rate": 1.0,
        "overrefuse_miss": 0,
        "overrefuse_ok_n": 3,
        "overrefuse_n": 3,
        "named_intent_false_hit": 0,
        "named_ok_n": 12,
        "named_n": 12,
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
        "modes_visible": sorted(AZ0_MODES),
        "modes_n": 4,
        "named_fh_neq_heldout": True,
        "bank_stuff_forbidden": True,
        "regression_hold": True,
    }
    base.update(over)
    return base


def test_given_contract_when_constants_then_match_az1() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AZ1 — held-out FH + over-refuse
    assert PRODGEN_ID == "H-PRODGEN"
    assert "held-out" in PRODGEN_THESIS.lower() or "div" in PRODGEN_THESIS.lower()
    assert "gibberish-tail" in PRODGEN_CLAIM
    assert len(HELDOUT_FP_ROWS) >= 12
    assert len(OVERREFUSE_ROWS) >= 3
    assert len(NAMED_INTENT_ROWS) >= 12
    assert len(HARD_NATURAL_ROWS) >= 15
    bars = bars_from_gen_charter(AZ0_PRODUCT_GEN_CHARTER)
    assert int(bars["heldout_false_hit_max"]) == 0
    assert int(bars["overrefuse_miss_max"]) == 0
    assert int(bars["named_intent_false_hit_max"]) == 0
    assert float(bars["hard_natural_para_hit_min"]) >= 0.70
    assert bars["default_ask_exact_gold"] == "LOOKUP"
    assert bars["bank_stuff_forbidden"] is True
    assert bars["named_fh_neq_heldout"] is True


def test_given_heldout_lookup_when_score_then_false_hit() -> None:
    assert intent_false_hit(
        {
            "product_mode": "LOOKUP",
            "mode": "SEMWRAP_LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        }
    )


def test_given_overrefuse_when_score_then_lookup_clear_ok() -> None:
    assert overrefuse_row_ok(
        {
            "product_mode": "LOOKUP",
            "mode": "WRAP_LOOKUP",
            "completion": "a.clear()",
        }
    )
    assert overrefuse_miss(
        {
            "product_mode": "ABSTAIN",
            "mode": "NO_ANSWER",
            "completion": "NO_ANSWER",
        }
    )
    assert not overrefuse_row_ok(
        {
            "product_mode": "LOOKUP",
            "mode": "SEMWRAP_LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        }
    )


def test_given_heldout_traps_when_contrast_then_reject_div_sub_entropy() -> None:
    # GIVEN/WHEN/THEN: AZ1 held-out gate — wrong gold must reject
    assert contrastive_reject(
        "Write a short Python function named div that returns the "
        "quotient of two integers a and b.",
        "Write a short Python function named add that returns the sum "
        "of two integers a and b.",
        "def add(a, b):\n    return a + b",
    )
    assert contrastive_reject(
        "Write a short Python function named sub that returns a minus b "
        "for two integers.",
        "Write a short Python function named add that returns the sum "
        "of two integers a and b.",
        "def add(a, b):\n    return a + b",
    )
    assert contrastive_reject(
        "BIP-39: how many bits of entropy does a 12-word mnemonic use?",
        "BIP-39: mnemonic entropy length ENT must be a multiple of "
        "how many bits?",
        "32",
    )
    # Exact clear must NOT reject (over-refuse fix)
    assert not contrastive_reject(
        "Remove all items from list `a` — one method call.",
        "Remove all items from list `a` — one method call.",
        "a.clear()",
    )
    assert not contrastive_reject(
        "How do I clear every element from Python list a in one method call?",
        "Remove all items from list `a` — one method call.",
        "a.clear()",
    )


def test_given_heldout_ask_when_must_abstain_then_true() -> None:
    assert intent_ask_must_abstain(
        "Write a short Python function named div that returns the "
        "quotient of two integers a and b."
    )
    assert intent_ask_must_abstain(
        "BIP-39: how many bits of entropy does a 12-word mnemonic use?"
    )
    assert not intent_ask_must_abstain(
        "How do I clear every element from Python list a in one method call?"
    )
    # AY false-friend: remove≠clear must still abstain (named hold)
    assert intent_ask_must_abstain(
        "Python: remove x from my list a — I do not want a.clear()."
    )
    assert contrastive_reject(
        "Python: remove x from my list a — I do not want a.clear().",
        "Remove all items from list `a` — one method call.",
        "a.clear()",
    )


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_prodgen(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert PRODGEN_ID in out


def test_given_heldout_fh_when_decide_then_kill() -> None:
    out = decide_prodgen(
        board=_board(heldout_false_hit=1, heldout_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "heldout" in out.lower()


def test_given_overrefuse_miss_when_decide_then_kill() -> None:
    out = decide_prodgen(
        board=_board(overrefuse_miss=1, overrefuse_ok_n=2),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "overrefuse" in out.lower()


def test_given_named_fh_when_decide_then_kill() -> None:
    out = decide_prodgen(
        board=_board(named_intent_false_hit=1, named_ok_n=11),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "named" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_prodgen(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_rows_when_extract_then_heldout_and_orf_zero() -> None:
    heldout = [
        {"id": f"AZ-HFP-{i:02d}", "product_mode": "ABSTAIN", "mode": "NO_ANSWER"}
        for i in range(1, 13)
    ]
    orf = [
        {
            "id": f"AZ-ORF-{i:02d}",
            "product_mode": "LOOKUP",
            "mode": "WRAP_LOOKUP",
            "completion": "a.clear()",
        }
        for i in range(1, 4)
    ]
    named = [
        {"id": f"AY-IFP-{i:02d}", "product_mode": "ABSTAIN", "mode": "NO_ANSWER"}
        for i in range(1, 13)
    ]
    board = extract_prodgen_board(
        heldout_rows=heldout,
        overrefuse_rows=orf,
        named_rows=named,
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
    assert board["heldout_false_hit"] == 0
    assert board["overrefuse_miss"] == 0
    assert board["named_intent_false_hit"] == 0
    assert board["hard_natural_para_hit"] == 1.0
    assert board["modes_n"] == 4
