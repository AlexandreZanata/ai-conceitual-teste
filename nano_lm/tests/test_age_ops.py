"""
Contract: age layers map ages to buckets; H-AGE decision vs H-SEL.
GIVEN ages and ascending limits
WHEN layer_of_age / bucket_by_layer run
THEN indices land in the correct layer.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from age_ops import (
    bucket_by_layer,
    child_age,
    default_age_limits,
    layer_of_age,
)
from matrix_report_lib import decision


def test_given_limits_when_layer_of_age_then_buckets():
    limits = [2, 10**9]
    assert layer_of_age(0, limits) == 0
    assert layer_of_age(1, limits) == 0
    assert layer_of_age(2, limits) == 1


def test_given_ages_when_bucket_then_groups():
    assert bucket_by_layer([0, 2, 1, 5], [2, 10**9]) == [[0, 2], [1, 3]]


def test_given_parents_when_child_age_then_one_plus_max():
    assert child_age([1, 3]) == 4
    assert child_age([]) == 0


def test_given_layers_when_defaults_then_ascending():
    assert default_age_limits(2, step=2) == [2, 10**9]
    assert default_age_limits(3, step=2) == [2, 4, 10**9]


def test_given_better_than_hsel_when_hage_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-AGE", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hage_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-AGE", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
