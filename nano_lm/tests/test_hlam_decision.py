"""
Contract: H-LAM decision kills on unstable or ≤ H-BAL.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision


def test_given_unstable_when_hlam_then_kill():
    stats = {"H-BAL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "unstable": 1.0}
    assert decision("H-LAM", s, stats) == "KILL (unstable)"


def test_given_better_than_hbal_when_hlam_then_promote():
    stats = {"H-BAL": {"mean_lp": -17.4}}
    s = {"mean_lp": -17.0, "unstable": 0.0}
    assert decision("H-LAM", s, stats) == "PROMOTE (beats H-BAL)"


def test_given_worse_than_hbal_when_hlam_then_kill():
    stats = {"H-BAL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.5, "unstable": 0.0}
    assert decision("H-LAM", s, stats) == "KILL (≤ H-BAL)"
