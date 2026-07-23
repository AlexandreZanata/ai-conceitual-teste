"""
Contract: formal H-LAM vs H-BAL (unstable kills; else need > H-BAL).
GIVEN formal stats for H-LAM and H-BAL
WHEN decide_formal_vs_control runs
THEN PROMOTE confirmed iff H-LAM lp > H-BAL and unstable clear.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from formal_ops import decide_formal_vs_control, means_by_family


def test_given_unstable_when_formal_then_kill():
    stats = {
        "H-BAL": {
            "lp": -17.0, "wall": 100.0, "n": 3.0, "overfit": 0.0,
            "collapsed": 0.0, "unstable": 0.0,
        },
        "H-LAM": {
            "lp": -16.0, "wall": 90.0, "n": 3.0, "overfit": 0.0,
            "collapsed": 0.0, "unstable": 1.0,
        },
    }
    assert decide_formal_vs_control("H-LAM", "H-BAL", stats) == (
        "KILL (unstable; H-LAM)"
    )


def test_given_better_hlam_when_formal_then_promote():
    stats = {
        "H-BAL": {
            "lp": -17.0, "wall": 100.0, "n": 3.0, "overfit": 0.0,
            "collapsed": 0.0, "unstable": 0.0,
        },
        "H-LAM": {
            "lp": -16.5, "wall": 90.0, "n": 3.0, "overfit": 0.0,
            "collapsed": 0.0, "unstable": 0.0,
        },
    }
    assert decide_formal_vs_control("H-LAM", "H-BAL", stats) == (
        "PROMOTE confirmed (H-LAM > H-BAL)"
    )


def test_given_worse_hlam_when_formal_then_reverse():
    stats = {
        "H-BAL": {
            "lp": -16.0, "wall": 100.0, "n": 3.0, "overfit": 0.0,
            "collapsed": 0.0, "unstable": 0.0,
        },
        "H-LAM": {
            "lp": -17.0, "wall": 90.0, "n": 3.0, "overfit": 0.0,
            "collapsed": 0.0, "unstable": 0.0,
        },
    }
    assert decide_formal_vs_control("H-LAM", "H-BAL", stats) == (
        "KILL / reverse smoke (H-LAM ≤ H-BAL)"
    )


def test_given_unstable_row_when_means_then_flag():
    rows = [
        {"family": "H-LAM", "teacher_mean_logprob": -16.0, "unstable": True},
        {"family": "H-LAM", "teacher_mean_logprob": -17.0, "unstable": False},
    ]
    assert means_by_family(rows)["H-LAM"]["unstable"] == 1.0
