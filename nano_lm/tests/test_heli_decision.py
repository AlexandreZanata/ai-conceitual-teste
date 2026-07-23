"""
Contract: H-ELI decision kills on diversity collapse or ≤ H-SEL.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision


def test_given_collapse_when_heli_then_kill():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "collapsed": 1.0}
    assert decision("H-ELI", s, stats) == "KILL (diversity collapse)"


def test_given_better_than_hsel_when_heli_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "collapsed": 0.0}
    assert decision("H-ELI", s, stats) == "PROMOTE (beats H-SEL, diversity ok)"


def test_given_worse_than_hsel_when_heli_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "collapsed": 0.0}
    assert decision("H-ELI", s, stats) == "KILL / hold (≤ H-SEL)"
