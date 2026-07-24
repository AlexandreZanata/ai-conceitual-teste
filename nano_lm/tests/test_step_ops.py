"""
Contract: H-STEP plateau + decide vs H-CURL2 tip.
"""

from __future__ import annotations

from step_ops import decide_hstep, improved, should_stop


def test_given_higher_lp_when_improved_then_true():
    assert improved(-10.0, -12.0, min_delta=0.01)
    assert not improved(-12.0, -12.0, min_delta=0.01)
    assert not improved(-11.995, -12.0, min_delta=0.01)


def test_given_bad_streak_when_patience_then_stop():
    assert not should_stop(1, patience=2)
    assert should_stop(2, patience=2)


def test_given_ge_tip_when_decide_then_promote():
    stats = {"H-CURL2": {"mean_lp": -16.5}}
    assert decide_hstep({"mean_lp": -16.5}, stats).startswith("PROMOTE")
    assert decide_hstep({"mean_lp": -16.4}, stats).startswith("PROMOTE")


def test_given_worse_lp_when_decide_then_kill():
    stats = {"H-CURL2": {"mean_lp": -16.5}}
    assert "worse" in decide_hstep({"mean_lp": -16.7}, stats)
