"""Contract: Wave AU1 H-PRODHARD — live-audit debts (pesquisa §5)."""

from __future__ import annotations

from au_session_ops import AU0_MODES, AU0_PRODUCT_DEBT_SUITE
from prodhard_ops import (
    PRODHARD_CLAIM,
    PRODHARD_ID,
    PRODHARD_THESIS,
    bars_from_debt_suite,
    decide_prodhard,
    extract_prodhard_board,
    human_para_hit,
    near_miss_ok,
    peak_ok,
    peak_span_usable,
)


def _board(**over: object) -> dict:
    base = {
        "para_hit": 0.875,
        "para_n_true": 7,
        "para_n": 8,
        "false_hit": 0,
        "near_miss_ok": True,
        "near_miss_mode": "ABSTAIN",
        "peak_ok": True,
        "peak_mode": "PEAK",
        "peak_completion": "Ownership is a set of rules that govern memory.",
        "known_lookup_ok": True,
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0},
            "PEAK": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.03},
            "DECODE": {"p50_wall_ms": 10.0, "p99_wall_ms": 12.0},
            "ABSTAIN": {"p50_wall_ms": 90.0, "p99_wall_ms": 110.0},
        },
        "kb_coverage_pct": 100.0,
        "kb_hole_list": ["example-hole"],
        "modes_visible": sorted(AU0_MODES),
        "modes_n": 4,
    }
    base.update(over)
    return base


def test_given_contract_when_constants_then_match_au1() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AU1 — close live-audit debts
    assert PRODHARD_ID == "H-PRODHARD"
    assert "near-miss" in PRODHARD_THESIS.lower() or "live-audit" in PRODHARD_THESIS.lower()
    assert "snippet-prefix" in PRODHARD_CLAIM
    bars = bars_from_debt_suite(AU0_PRODUCT_DEBT_SUITE)
    assert float(bars["para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert bars["default_ask_near_miss"] == "ABSTAIN"


def test_given_near_miss_lookup_cs_when_check_then_fail() -> None:
    bad = {
        "product_mode": "LOOKUP",
        "mode": "SEMWRAP_LOOKUP",
        "completion": "CS = ENT / 32",
    }
    assert near_miss_ok(bad) is False
    good = {
        "product_mode": "ABSTAIN",
        "mode": "NO_ANSWER",
        "completion": "NO_ANSWER",
    }
    assert near_miss_ok(good) is True


def test_given_peak_fragment_when_usable_then_false() -> None:
    assert peak_span_usable("mory while running") is False
    assert peak_span_usable(
        "Ownership is a set of rules that govern how a Rust program "
        "manages memory."
    )


def test_given_peak_payload_when_ok_then_usable_or_abstain() -> None:
    assert peak_ok(
        {
            "mode": "PEAK_FAST+GENBASE",
            "product_mode": "PEAK",
            "completion": (
                "Ownership is a set of rules that govern how a Rust "
                "program manages memory."
            ),
        }
    )
    assert peak_ok(
        {"mode": "NO_ANSWER", "product_mode": "ABSTAIN", "completion": "NO_ANSWER"}
    )
    assert not peak_ok(
        {
            "mode": "PEAK_FAST+GENBASE",
            "product_mode": "PEAK",
            "completion": "mory while running",
        }
    )


def test_given_add_lookup_when_hit_then_true() -> None:
    assert human_para_hit(
        {
            "mode": "SEMWRAP_LOOKUP",
            "product_mode": "LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        }
    )
    assert not human_para_hit(
        {"mode": "NO_ANSWER", "product_mode": "ABSTAIN", "completion": "NO_ANSWER"}
    )


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_prodhard(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert PRODHARD_ID in out


def test_given_near_miss_fail_when_decide_then_kill() -> None:
    out = decide_prodhard(
        board=_board(near_miss_ok=False, false_hit=1), anti_fp_signed=True
    )
    assert out.startswith("KILL")
    assert "near-miss" in out


def test_given_low_para_when_decide_then_hold() -> None:
    out = decide_prodhard(
        board=_board(para_hit=0.5, para_n_true=4, para_n=8),
        anti_fp_signed=True,
    )
    assert out.startswith("HOLD")
    assert "para_hit" in out


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_prodhard(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_extract_when_build_then_publishes_metrics() -> None:
    board = extract_prodhard_board(
        para_hits=[True, True, False, True, True, True, True, True],
        near={
            "product_mode": "ABSTAIN",
            "mode": "NO_ANSWER",
            "completion": "NO_ANSWER",
        },
        peak={
            "mode": "PEAK_FAST+GENBASE",
            "product_mode": "PEAK",
            "completion": "Ownership is a set of rules that govern memory.",
        },
        known={
            "mode": "WRAP_LOOKUP",
            "product_mode": "LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        },
        metrics={
            "paths": {
                "LOOKUP": {"stats": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0}},
                "PEAK": {"stats": {"p50_wall_ms": 1.0, "p99_wall_ms": 2.0}},
                "DECODE": {"stats": {"p50_wall_ms": 10.0, "p99_wall_ms": 12.0}},
                "ABSTAIN": {"stats": {"p50_wall_ms": 5.0, "p99_wall_ms": 6.0}},
            },
            "kb": {"snap": {"coverage_pct": 99.0, "holes": ["h1"]}},
        },
        ship={
            "arms": [
                {"product_mode": "LOOKUP"},
                {"product_mode": "PEAK"},
                {"product_mode": "DECODE"},
                {"product_mode": "ABSTAIN"},
            ]
        },
    )
    assert board["para_hit"] == 0.875
    assert board["false_hit"] == 0
    assert board["near_miss_ok"] is True
    assert board["peak_ok"] is True
    assert board["kb_coverage_pct"] == 99.0
    assert set(board["modes_visible"]) == AU0_MODES
