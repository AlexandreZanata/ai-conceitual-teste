"""
Contract: anti-selection parents are the worst half; H-ANTI decision vs H-SEL.
GIVEN fitness scores
WHEN anti_parent_indices runs
THEN return the lowest-fitness half (ties prefer higher index as worse).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from anti_ops import anti_parent_indices
from matrix_report_lib import decision


def test_given_pop4_when_anti_then_worst_half():
    fits = [-1.0, -10.0, -2.0, -9.0]
    assert anti_parent_indices(fits) == [1, 3]


def test_given_tie_when_anti_then_higher_index_worse():
    fits = [-5.0, -5.0, -1.0]
    # n//2 = 1; both 0 and 1 tied at -5; higher index (1) ranks worse first
    assert anti_parent_indices(fits) == [1]


def test_given_empty_when_anti_then_raises():
    try:
        anti_parent_indices([])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_better_than_hsel_when_hanti_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-ANTI", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hanti_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-ANTI", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
