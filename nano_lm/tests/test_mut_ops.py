"""
Contract: 1/5 success rule adapts mutate scale; H-MUT decision vs H-SEL.
GIVEN scale and a success/failure signal
WHEN adapt_mutate_scale runs
THEN success multiplies by factor; failure divides; result stays in bounds.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from mut_ops import adapt_mutate_scale, fitness_improved


def test_given_success_when_adapt_then_scale_grows():
    assert adapt_mutate_scale(0.02, True, factor=1.2) == pytest.approx(0.024)


def test_given_failure_when_adapt_then_scale_shrinks():
    assert adapt_mutate_scale(0.02, False, factor=1.2) == pytest.approx(0.02 / 1.2)


def test_given_bounds_when_adapt_then_clips():
    assert adapt_mutate_scale(0.4, True, factor=2.0, lo=1e-4, hi=0.5) == pytest.approx(0.5)
    assert adapt_mutate_scale(1e-4, False, factor=2.0, lo=1e-4, hi=0.5) == pytest.approx(1e-4)


def test_given_delta_when_improved_then_true_false():
    assert fitness_improved(-10.0, -9.5) is True
    assert fitness_improved(-9.5, -9.5) is False
    assert fitness_improved(-9.0, -9.5) is False


def test_given_better_than_hsel_when_hmut_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-MUT", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hmut_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-MUT", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
