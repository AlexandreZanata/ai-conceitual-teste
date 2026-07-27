"""Contract: Wave AW1 H-PRODKEEP — Caminho A keep under pressure (pesquisa §2)."""

from __future__ import annotations

from aw_session_ops import AW0_MODES, AW0_PRODUCT_KEEP_CHARTER
from prodkeep_ops import (
    PRESSURE_PARA_ROWS,
    PRODKEEP_CLAIM,
    PRODKEEP_ID,
    PRODKEEP_THESIS,
    bars_from_keep_charter,
    decide_prodkeep,
    decode_content_honest,
    extract_prodkeep_board,
    gate_junk_decode,
    human_para_hit,
    near_miss_ok,
)


def _board(**over: object) -> dict:
    base = {
        "para_hit": 0.85,
        "para_n_true": 17,
        "para_n": 20,
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
        "modes_visible": sorted(AW0_MODES),
        "modes_n": 4,
        "regression_hold": True,
    }
    base.update(over)
    return base


def test_given_contract_when_constants_then_match_aw1() -> None:
    # GIVEN/WHEN/THEN: pesquisa §2 AW1 — hold Caminho A under pressure-para
    assert PRODKEEP_ID == "H-PRODKEEP"
    assert "pressure" in PRODKEEP_THESIS.lower()
    assert "gibberish-tail" in PRODKEEP_CLAIM
    assert len(PRESSURE_PARA_ROWS) >= 20
    bars = bars_from_keep_charter(AW0_PRODUCT_KEEP_CHARTER)
    assert float(bars["para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0
    assert int(bars["pressure_para_min_n"]) >= 20
    assert bars["decode_gibberish_neq_content_ok"] is True
    assert bars["default_ask_near_miss"] == "ABSTAIN"
    assert bars["regression_hold"] is True


def test_given_gibberish_decode_when_gate_then_abstain() -> None:
    raw = {
        "mode": "WRAP_DECODE",
        "product_mode": "DECODE",
        "completion": (
            "quickly and which,.Suddenly some \ufffd funny everything "
            "really carefully looking something"
        ),
        "wall_ms": 100.0,
        "n_new": 64,
    }
    assert decode_content_honest(raw) is False
    gated = gate_junk_decode(raw)
    assert gated["product_mode"] == "ABSTAIN"
    assert gated["completion"] == "NO_ANSWER"
    assert decode_content_honest(gated) is True


def test_given_near_miss_when_lookup_cs_then_fail() -> None:
    assert near_miss_ok(
        {
            "product_mode": "LOOKUP",
            "mode": "SEMWRAP_LOOKUP",
            "completion": "CS = ENT / 32",
        }
    ) is False
    assert near_miss_ok(
        {
            "product_mode": "ABSTAIN",
            "mode": "NO_ANSWER",
            "completion": "NO_ANSWER",
        }
    ) is True


def test_given_add_lookup_when_hit_then_true() -> None:
    assert human_para_hit(
        {
            "mode": "SEMWRAP_LOOKUP",
            "product_mode": "LOOKUP",
            "completion": "def add(a, b):\n    return a + b",
        }
    )


def test_given_all_ok_when_decide_then_promote() -> None:
    out = decide_prodkeep(board=_board(), anti_fp_signed=True)
    assert out.startswith("PROMOTE")
    assert PRODKEEP_ID in out


def test_given_decode_debt_open_when_decide_then_kill() -> None:
    out = decide_prodkeep(
        board=_board(decode_content_ok=False), anti_fp_signed=True
    )
    assert out.startswith("KILL")
    assert "DECODE" in out


def test_given_low_para_when_decide_then_hold() -> None:
    out = decide_prodkeep(
        board=_board(para_hit=0.5, para_n_true=10, para_n=20),
        anti_fp_signed=True,
    )
    assert out.startswith("HOLD")
    assert "para" in out.lower()


def test_given_short_para_n_when_decide_then_kill() -> None:
    out = decide_prodkeep(
        board=_board(para_n=8, para_n_true=8, para_hit=1.0),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "para" in out.lower()


def test_given_unsigned_when_decide_then_kill() -> None:
    out = decide_prodkeep(board=_board(), anti_fp_signed=False)
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_extract_when_build_then_publishes_metrics() -> None:
    board = extract_prodkeep_board(
        para_hits=[True] * 17 + [False] * 3,
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
        decode={
            "mode": "NO_ANSWER",
            "product_mode": "ABSTAIN",
            "completion": "NO_ANSWER",
            "abstained": True,
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
        ship={"arms": []},
    )
    assert board["para_hit"] == 0.85
    assert board["false_hit"] == 0
    assert board["decode_content_ok"] is True
    assert board["kb_coverage_pct"] == 99.0
    assert board["regression_hold"] is True
    assert set(board["modes_visible"]) == AW0_MODES
