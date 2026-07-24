"""
Contract: H-CURD stage/frac + decide vs H-CURL2.
"""

from __future__ import annotations

from curd_ops import curd_stage, decide_hcurd, easy_frac


def test_given_steps_when_stage_then_ramps():
    stages = [curd_stage(i, 30, n_stages=3) for i in range(30)]
    assert stages[0] == 0
    assert stages[-1] == 2
    assert set(stages) == {0, 1, 2}


def test_given_stage_when_frac_then_increasing():
    assert easy_frac(0, n_stages=3) == 1.0 / 3.0
    assert easy_frac(2, n_stages=3) == 1.0


def test_given_better_lp_when_decide_then_promote():
    stats = {"H-CURL2": {"mean_lp": -16.7}}
    assert decide_hcurd({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_worse_lp_when_decide_then_kill():
    stats = {"H-CURL2": {"mean_lp": -16.5}}
    assert "≤ H-CURL2" in decide_hcurd({"mean_lp": -16.7}, stats)
