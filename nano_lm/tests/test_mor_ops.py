"""
Contract: soft mortality culls worst quartile; H-MOR decision vs H-SEL.
GIVEN fitness scores
WHEN cull_worst runs with k
THEN the k lowest-fitness indices are culled and the rest survive.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from mor_ops import cull_worst, mortality_k


def test_given_pop4_when_mortality_k_then_one():
    assert mortality_k(4) == 1
    assert mortality_k(8) == 2


def test_given_fits_when_cull_then_worst_removed():
    fits = [-10.0, -1.0, -5.0, -8.0]
    survivors, culled = cull_worst(fits, 1)
    assert culled == [0]
    assert survivors == [1, 2, 3]


def test_given_ties_when_cull_then_higher_index_dies():
    fits = [1.0, 1.0, 2.0]
    survivors, culled = cull_worst(fits, 1)
    assert culled == [1]
    assert survivors == [0, 2]


def test_given_k_too_large_when_cull_then_raises():
    with pytest.raises(ValueError):
        cull_worst([1.0, 2.0], 2)


def test_given_better_than_hsel_when_hmor_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-MOR", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hmor_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-MOR", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
