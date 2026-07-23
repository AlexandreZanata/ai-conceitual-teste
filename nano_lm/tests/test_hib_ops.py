"""
Contract: hibernation schedule + decay inherit; H-HIB decision vs H-SEL.
GIVEN generation and parent fits
WHEN should_hibernate / inherit_fits run
THEN gen0 never hibernates; decayed fits = parent × decay.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hib_ops import decay_fit, inherit_fits, should_hibernate
from matrix_report_lib import decision


def test_given_period_when_hibernate_then_skip_gen0():
    assert should_hibernate(0, 2) is False
    assert should_hibernate(1, 2) is True
    assert should_hibernate(2, 2) is False
    with pytest.raises(ValueError):
        should_hibernate(1, 0)


def test_given_parent_when_decay_then_scaled():
    assert decay_fit(-10.0, 0.9) == pytest.approx(-9.0)
    with pytest.raises(ValueError):
        decay_fit(-1.0, 0.0)


def test_given_parents_when_inherit_then_list():
    assert inherit_fits([-10.0, -20.0], 0.5) == pytest.approx([-5.0, -10.0])


def test_given_better_than_hsel_when_hhib_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-HIB", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hhib_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-HIB", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
