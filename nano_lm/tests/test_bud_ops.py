"""Contract: H-BUD hard wall/GFLOPs (ms/step) budget survivors."""

from __future__ import annotations

from bud_ops import (
    decide_hbud,
    survive_decode,
    survive_train,
    within_gflops_budget,
    within_ms_step_budget,
    within_wall_budget,
)


def test_given_wall_and_gflops_ok_when_survive_decode_then_survive() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 20.0, "mean_tps": 800.0, "mean_gflops": 10.0}
    util = {"mean_lp": -11.9, "mean_wall": 5.0, "mean_tps": 3000.0, "mean_gflops": 10.0}
    assert survive_decode(util, tip).startswith("SURVIVE")
    assert within_wall_budget(util, tip)
    assert within_gflops_budget(util, tip)


def test_given_gflops_inflate_when_survive_decode_then_kill() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 20.0, "mean_tps": 800.0, "mean_gflops": 10.0}
    util = {"mean_lp": -11.9, "mean_wall": 5.0, "mean_tps": 3000.0, "mean_gflops": 40.0}
    assert "GFLOPs" in survive_decode(util, tip)


def test_given_wall_over_when_survive_decode_then_kill() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 5.0, "mean_tps": 800.0, "mean_gflops": 10.0}
    util = {"mean_lp": -11.9, "mean_wall": 6.0, "mean_tps": 3000.0, "mean_gflops": 10.0}
    assert "wall over" in survive_decode(util, tip)


def test_given_ms_step_win_when_survive_train_then_survive() -> None:
    tip = {"mean_lp": -13.0, "mean_ms_step": 19.0}
    util = {"mean_lp": -12.5, "mean_ms_step": 14.0}
    assert survive_train(util, tip).startswith("SURVIVE")
    assert within_ms_step_budget(util, tip)


def test_given_quality_drop_when_survive_train_then_kill() -> None:
    tip = {"mean_lp": -13.0, "mean_ms_step": 19.0}
    util = {"mean_lp": -13.2, "mean_ms_step": 14.0}
    assert "quality drop" in survive_train(util, tip)


def test_given_one_survivor_when_decide_then_promote() -> None:
    v = {
        "H-PACK": "SURVIVE (wall+GFLOPs budgets + win)",
        "H-QPACK": "KILL (GFLOPs over tip budget)",
        "H-TPACK": "KILL (quality drop under budget)",
    }
    assert decide_hbud(v).startswith("PROMOTE")
    assert "H-PACK" in decide_hbud(v)


def test_given_no_survivor_when_decide_then_kill() -> None:
    v = {
        "H-PACK": "KILL (GFLOPs over tip budget)",
        "H-QPACK": "KILL (wall over tip budget)",
        "H-TPACK": "KILL (no ms/step win under budget)",
    }
    assert decide_hbud(v).startswith("KILL")


def test_given_missing_when_decide_then_needs() -> None:
    assert decide_hbud({}).startswith("needs H-PACK")
