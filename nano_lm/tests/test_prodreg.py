"""Contract: Wave AT1 H-PRODREG — Caminho A regression bars (pesquisa §5)."""

from __future__ import annotations

from at_session_ops import AT0_MODES, AT0_PRODREG_SUITE
from prodreg_ops import (
    PRODREG_CLAIM,
    PRODREG_ID,
    PRODREG_PILLARS,
    PRODREG_THESIS,
    bars_from_suite,
    decide_prodreg,
    extract_prodreg_metrics,
    pillar_pass,
)


def _board(**over: object) -> dict:
    base = {
        "para_hit": 0.80,
        "para_n_true": 16,
        "para_n": 20,
        "false_hit": 0,
        "false_hit_ids": [],
        "latency": {
            "LOOKUP": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0},
            "PEAK": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.03},
            "DECODE": {"p50_wall_ms": 10.0, "p99_wall_ms": 12.0},
            "ABSTAIN": {"p50_wall_ms": 90.0, "p99_wall_ms": 110.0},
        },
        "kb_coverage_pct": 100.0,
        "kb_hole_list": ["example-hole"],
        "modes_visible": sorted(AT0_MODES),
        "modes_n": 4,
        "default_ask_abstain_rate": 1.0,
        "askabstain_known_ok": True,
    }
    base.update(over)
    return base


def _pillars(**over: str) -> dict[str, str]:
    base = {name: "PROMOTE" for name in PRODREG_PILLARS}
    base.update(over)
    return base


def test_given_contract_when_constants_then_match_at1() -> None:
    # GIVEN/WHEN/THEN: pesquisa §5 AT1 — Caminho A bars
    assert PRODREG_ID == "H-PRODREG"
    assert set(PRODREG_PILLARS) == {
        "askabstain",
        "advsafe",
        "paraext2",
        "metrics",
        "shipui",
    }
    assert "regression" in PRODREG_THESIS.lower() or "Caminho" in PRODREG_THESIS
    assert "not open chat" in PRODREG_CLAIM.lower()
    bars = bars_from_suite(AT0_PRODREG_SUITE)
    assert float(bars["para_hit_min"]) >= 0.70
    assert int(bars["false_hit_max"]) == 0


def test_given_all_promote_when_decide_then_promote() -> None:
    out = decide_prodreg(
        pillars=_pillars(), metrics_board=_board(), anti_fp_signed=True
    )
    assert out.startswith("PROMOTE")
    assert PRODREG_ID in out


def test_given_false_hit_when_decide_then_kill() -> None:
    out = decide_prodreg(
        pillars=_pillars(),
        metrics_board=_board(false_hit=1),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "false_hit" in out


def test_given_advsafe_kill_when_decide_then_kill() -> None:
    out = decide_prodreg(
        pillars=_pillars(advsafe="KILL (FH)"),
        metrics_board=_board(),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "advsafe" in out


def test_given_para_hold_when_decide_then_hold() -> None:
    out = decide_prodreg(
        pillars=_pillars(paraext2="HOLD (hit 0.65)"),
        metrics_board=_board(para_hit=0.65),
        anti_fp_signed=True,
    )
    assert out.startswith("HOLD")
    assert "paraext2" in out


def test_given_low_para_board_when_decide_then_hold() -> None:
    out = decide_prodreg(
        pillars=_pillars(),
        metrics_board=_board(para_hit=0.65),
        anti_fp_signed=True,
    )
    assert out.startswith("HOLD")
    assert "para_hit" in out


def test_given_unsigned_anti_fp_when_decide_then_kill() -> None:
    out = decide_prodreg(
        pillars=_pillars(),
        metrics_board=_board(),
        anti_fp_signed=False,
    )
    assert out.startswith("KILL")
    assert "anti-FP" in out


def test_given_missing_modes_when_decide_then_kill() -> None:
    out = decide_prodreg(
        pillars=_pillars(),
        metrics_board=_board(modes_visible=["LOOKUP", "DECODE"]),
        anti_fp_signed=True,
    )
    assert out.startswith("KILL")
    assert "modes" in out


def test_given_summaries_when_extract_then_board_fields() -> None:
    para = {
        "stats": {
            "hit_rate": 0.8,
            "n_true_hit": 16,
            "n_trials": 20,
        }
    }
    adv = {"stats": {"n_false_hit": 0}, "false_hit_ids": []}
    metrics = {
        "paths": {
            "LOOKUP": {"stats": {"p50_wall_ms": 0.0, "p99_wall_ms": 0.0}},
            "PEAK": {"stats": {"p50_wall_ms": 0.02, "p99_wall_ms": 0.03}},
        },
        "kb": {"snap": {"coverage_pct": 100.0, "holes": ["h1"]}},
    }
    ask = {
        "stats": {
            "ood_abstain_rate": 1.0,
            "known_lookup_ok": True,
        }
    }
    ship = {
        "arms": [
            {"product_mode": "LOOKUP"},
            {"product_mode": "PEAK"},
            {"product_mode": "DECODE"},
            {"product_mode": "ABSTAIN"},
        ]
    }
    board = extract_prodreg_metrics(
        para=para, adv=adv, metrics=metrics, ask=ask, ship=ship
    )
    assert board["para_hit"] == 0.8
    assert board["false_hit"] == 0
    assert board["kb_coverage_pct"] == 100.0
    assert board["kb_hole_list"] == ["h1"]
    assert set(board["modes_visible"]) == AT0_MODES
    assert pillar_pass("PROMOTE (x)")
    assert not pillar_pass("HOLD")
