"""
Contract: H-ALAT α/T schedule + decide vs H-CURL2 tip.
"""

from __future__ import annotations

from alat_ops import alat_alpha, alat_temp, decide_halat


def test_given_stages_when_alpha_then_ramps_up():
    assert alat_alpha(0, n_stages=3) == 0.25
    assert alat_alpha(2, n_stages=3) == 0.75
    assert alat_alpha(0, n_stages=3) < alat_alpha(1, n_stages=3)


def test_given_stages_when_temp_then_ramps_down():
    assert alat_temp(0, n_stages=3) == 3.0
    assert alat_temp(2, n_stages=3) == 1.0
    assert alat_temp(0, n_stages=3) > alat_temp(1, n_stages=3)


def test_given_better_lp_when_decide_then_promote():
    stats = {"H-CURL2": {"mean_lp": -16.7}}
    assert decide_halat({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_worse_lp_when_decide_then_kill():
    stats = {"H-CURL2": {"mean_lp": -16.5}}
    assert "≤ H-CURL2" in decide_halat({"mean_lp": -16.7}, stats)
