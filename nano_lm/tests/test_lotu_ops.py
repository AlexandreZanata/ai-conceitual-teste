"""
Contract: underdog gift maps worst→elite clone target; H-LOTU vs H-SEL.
GIVEN fitness scores
WHEN underdog_gift runs
THEN return distinct (underdog, elite) indices.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lotu_ops import best_index, underdog_gift, worst_index
from matrix_report_lib import decision


def test_given_fits_when_best_worst_then_extremes():
    fits = [-1.0, -10.0, -2.0]
    assert best_index(fits) == 0
    assert worst_index(fits) == 1


def test_given_fits_when_gift_then_under_gets_elite():
    assert underdog_gift([-1.0, -10.0, -2.0, -9.0]) == (1, 0)


def test_given_all_equal_when_gift_then_distinct():
    under, elite = underdog_gift([-5.0, -5.0, -5.0])
    assert under != elite


def test_given_better_than_hsel_when_hlotu_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-LOTU", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hlotu_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-LOTU", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
