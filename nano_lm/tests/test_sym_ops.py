"""
Contract: obligate pairs require both above mean; H-SYM decision vs H-SEL.
GIVEN fitness scores
WHEN eligible_above_mean / obligate_pairs run
THEN only above-mean indices pair; <2 eligible → no pairs.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from sym_ops import eligible_above_mean, mean_fitness, obligate_pairs


def test_given_fits_when_mean_then_average():
    assert mean_fitness([-1.0, -3.0]) == pytest.approx(-2.0)


def test_given_fits_when_eligible_then_above_mean():
    fits = [-1.0, -10.0, -2.0, -9.0]
    # mean = -5.5 → eligible 0 (-1) and 2 (-2)
    assert eligible_above_mean(fits) == [0, 2]


def test_given_two_eligible_when_pairs_then_one_pair():
    assert obligate_pairs([0, 2]) == [(0, 2)]


def test_given_three_eligible_when_pairs_then_leftover_with_first():
    assert obligate_pairs([0, 1, 2]) == [(0, 1), (2, 0)]


def test_given_singleton_when_pairs_then_sterile():
    assert obligate_pairs([3]) == []
    assert obligate_pairs([]) == []


def test_given_better_than_hsel_when_hsym_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-SYM", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hsym_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-SYM", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
