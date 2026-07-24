"""
Contract: H-THIN param cap + decide vs H-CURL same-decode.
"""

from __future__ import annotations

from student_model import THIN_MAX_PARAMS, build_thin_student, count_params
from thin_ops import decide_hthin


def test_given_thin_build_when_count_then_under_cap():
    n = count_params(build_thin_student())
    assert n <= THIN_MAX_PARAMS
    assert n < 3_000_000


def test_given_wall_win_quality_when_decide_then_promote():
    stats = {"H-CURL": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.45, "mean_wall": 40.0}
    assert decide_hthin(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-CURL": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.7, "mean_wall": 30.0}
    assert "quality drop" in decide_hthin(s, stats)


def test_given_no_wall_when_decide_then_kill():
    stats = {"H-CURL": {"mean_lp": -16.5, "mean_wall": 40.0}}
    s = {"mean_lp": -16.4, "mean_wall": 45.0}
    assert "no wall win" in decide_hthin(s, stats)
