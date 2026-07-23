"""
Contract: cosine vs linear schedules; H-ANN decision vs KD-cos.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from schedules import cosine_value, linear_value, schedule_pair


def test_given_endpoints_when_cosine_then_start_and_end():
    assert cosine_value(1.0, 0.1, 0.0) == pytest.approx(1.0)
    assert cosine_value(1.0, 0.1, 1.0) == pytest.approx(0.1)
    mid = cosine_value(1.0, 0.1, 0.5)
    assert 0.1 < mid < 1.0
    assert mid == pytest.approx(0.55)


def test_given_endpoints_when_linear_then_midpoint():
    assert linear_value(2.0, 1.0, 0.0) == pytest.approx(2.0)
    assert linear_value(2.0, 1.0, 1.0) == pytest.approx(1.0)
    assert linear_value(2.0, 1.0, 0.5) == pytest.approx(1.5)


def test_given_cosine_kind_when_pair_then_temp_fixed():
    lr, temp = schedule_pair(
        "cosine", 5, 11, lr_start=3e-4, lr_end=3e-5, temp_start=2.0, temp_end=1.0
    )
    assert temp == pytest.approx(2.0)
    assert 3e-5 < lr < 3e-4


def test_given_anneal_kind_when_pair_then_both_move():
    lr0, t0 = schedule_pair(
        "anneal", 0, 11, lr_start=3e-4, lr_end=3e-5, temp_start=2.0, temp_end=1.0
    )
    lr1, t1 = schedule_pair(
        "anneal", 10, 11, lr_start=3e-4, lr_end=3e-5, temp_start=2.0, temp_end=1.0
    )
    assert lr0 == pytest.approx(3e-4)
    assert t0 == pytest.approx(2.0)
    assert lr1 == pytest.approx(3e-5)
    assert t1 == pytest.approx(1.0)


def test_given_cosine_better_when_hann_then_kill():
    stats = {"KD-cos": {"mean_lp": -16.5}}
    s = {"mean_lp": -17.0}
    assert decision("H-ANN", s, stats) == "KILL (cosine wins)"


def test_given_anneal_better_when_hann_then_promote():
    stats = {"KD-cos": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.5}
    assert decision("H-ANN", s, stats) == "PROMOTE (beats cosine KD)"
