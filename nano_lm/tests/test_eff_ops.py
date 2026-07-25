"""Contract: H-EFF PACK efficiency PROMOTE/HOLD gate."""

from __future__ import annotations

from hold_ops import assert_disjoint, load_prompt_ids
from eff_ops import EPS_LP, at_quality_floor, decide_heff, domain_speed_win
from run_formal_heff import formal_cfg


def _fams(serve_lp: float, early_lp: float, wall: float, tps: float) -> dict:
    return {
        "H-EARLY": {"mean_lp": early_lp, "mean_wall": 20.0, "mean_tps": 600.0},
        "H-SERVE": {
            "mean_lp": serve_lp,
            "mean_wall": wall,
            "mean_tps": tps,
        },
    }


def test_given_floor_and_wall_down_when_decide_then_promote() -> None:
    stats = {"prog": _fams(-8.16, -8.16, 3.0, 1900.0)}
    out = decide_heff(stats)
    assert out.startswith("PROMOTE")
    assert "prog" in out


def test_given_floor_and_tps_up_when_decide_then_promote() -> None:
    stats = {"btc": _fams(-10.9, -10.9, 7.0, 2500.0)}
    out = decide_heff(stats)
    assert out.startswith("PROMOTE")
    assert "btc" in out


def test_given_no_speedup_when_decide_then_hold() -> None:
    stats = {"prog": _fams(-8.16, -8.16, 5.0, 1800.0)}
    out = decide_heff(stats)
    assert out.startswith("HOLD")


def test_given_floor_fail_when_decide_then_hold() -> None:
    stats = {"prog": _fams(-8.16 - EPS_LP - 0.1, -8.16, 1.0, 5000.0)}
    out = decide_heff(stats)
    assert out.startswith("HOLD")
    assert "floor-fail" in out


def test_given_helpers_when_check_then_bools() -> None:
    assert at_quality_floor(-8.16, -8.16)
    assert not at_quality_floor(-8.16 - EPS_LP - 0.01, -8.16)
    assert domain_speed_win(
        {"mean_wall": 3.0, "mean_tps": 1000.0},
        {"mean_wall": 4.0, "mean_tps": 1000.0},
    )


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    c = formal_cfg()
    assert "eval_prompts" in str(c["prompts"])
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert c["seeds"] == [0, 1, 2]
