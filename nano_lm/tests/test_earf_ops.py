"""
Contract: H-EARF FLOP-aware score + decide vs H-EARLY.
"""

from __future__ import annotations

from earf_ops import decide_hearf, flop_aware_score


def test_given_gflops_when_score_then_penalizes():
    a = flop_aware_score(-10.0, 1.0, 0.4)
    b = flop_aware_score(-10.0, 10.0, 0.4)
    assert a > b


def test_given_better_flops_when_decide_then_promote():
    stats = {
        "H-EARLY": {"mean_lp": -16.0, "mean_gflops": 9.0},
    }
    s = {"mean_lp": -16.0, "mean_gflops": 7.0}
    assert decide_hearf(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.0, "mean_gflops": 9.0}}
    s = {"mean_lp": -16.2, "mean_gflops": 5.0}
    assert "quality" in decide_hearf(s, stats)


def test_given_no_flop_win_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.0, "mean_gflops": 9.0}}
    s = {"mean_lp": -15.9, "mean_gflops": 9.5}
    assert "FLOP" in decide_hearf(s, stats)
