"""
Contract: catastrophe schedule + immigrant refill; H-CAT decision vs H-SEL.
GIVEN generation index and pop size
WHEN should_catastrophe / immigrant_count run
THEN wipe cadence and immigrant count match keep=1.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from cat_ops import elite_index, immigrant_count, should_catastrophe
from matrix_report_lib import decision


def test_given_period_when_catastrophe_then_multiples():
    assert should_catastrophe(0, 2) is False
    assert should_catastrophe(1, 2) is True
    assert should_catastrophe(3, 2) is True
    with pytest.raises(ValueError):
        should_catastrophe(0, 0)


def test_given_fits_when_elite_then_best_index():
    assert elite_index([-1.0, -10.0, -2.0]) == 0


def test_given_pop_when_immigrants_then_keep_one():
    assert immigrant_count(4, keep=1) == 3
    with pytest.raises(ValueError):
        immigrant_count(2, keep=0)


def test_given_better_than_hsel_when_hcat_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-CAT", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hcat_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-CAT", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
