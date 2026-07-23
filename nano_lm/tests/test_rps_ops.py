"""
Contract: RPS cyclic dominance + niche collapse; H-RPS decision vs H-SEL.
GIVEN niches in {0,1,2}
WHEN rps_beats / niche_adjusted_fitness run
THEN cyclic winners get bonus; single-niche pops are collapsed.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from rps_ops import (
    mutate_niche,
    niche_adjusted_fitness,
    niche_collapsed,
    rps_beats,
)


def test_given_cycle_when_beats_then_rps_order():
    assert rps_beats(0, 2) == 1
    assert rps_beats(1, 0) == 1
    assert rps_beats(2, 1) == 1
    assert rps_beats(0, 1) == -1
    assert rps_beats(1, 1) == 0


def test_given_niches_when_adjust_then_winner_bonus():
    raw = [0.0, 0.0, 0.0]
    # niches: 0 beats 2 only among {0,1,2} wait pop niches [0,1,2]
    # 0 beats 2 → 1 win; 1 beats 0 → 1 win; 2 beats 1 → 1 win
    out = niche_adjusted_fitness(raw, [0, 1, 2], bonus=0.5)
    assert out == pytest.approx([0.5, 0.5, 0.5])


def test_given_one_niche_when_collapsed_then_true():
    assert niche_collapsed([1, 1, 1]) is True
    assert niche_collapsed([0, 1, 0]) is False


def test_given_roll_when_mutate_niche_then_gate():
    assert mutate_niche(0, 0.9, p_mut=0.2) == 0
    assert mutate_niche(0, 0.1, p_mut=0.2) == 1


def test_given_collapse_when_hrps_then_kill():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "collapsed": 1.0}
    assert decision("H-RPS", s, stats) == "KILL (collapsed to 1 niche)"


def test_given_better_than_hsel_when_hrps_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "collapsed": 0.0}
    assert decision("H-RPS", s, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hrps_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "collapsed": 0.0}
    assert decision("H-RPS", s, stats) == "KILL / hold (≤ H-SEL)"
