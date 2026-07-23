"""
Contract: island split + ring migrate schedule; H-SPE decision vs H-SEL.
GIVEN pop size and island count
WHEN split_islands / should_migrate / ring_migrate_pairs run
THEN partitions cover all indices and migration fires on schedule.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from spe_ops import (
    best_in_island,
    ring_migrate_pairs,
    should_migrate,
    split_islands,
    worst_in_island,
)


def test_given_pop4_when_split2_then_equal_islands():
    assert split_islands(4, 2) == [[0, 1], [2, 3]]


def test_given_gen_when_migrate_every2_then_schedule():
    assert should_migrate(0, 2) is False
    assert should_migrate(1, 2) is True
    assert should_migrate(2, 2) is False


def test_given_islands_when_ring_then_cycle():
    assert ring_migrate_pairs(2) == [(0, 1), (1, 0)]


def test_given_fits_when_best_worst_then_extremes():
    fits = [-10.0, -1.0, -5.0]
    assert best_in_island(fits, [0, 1, 2]) == 1
    assert worst_in_island(fits, [0, 1, 2]) == 0


def test_given_better_than_hsel_when_hspe_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-SPE", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hspe_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-SPE", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
