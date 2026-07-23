"""
Contract: bank gene pick by proxy max; H-DECP must beat GLOBAL and B4.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from decp_ops import best_index, decide_hdecp


def test_given_scores_when_best_index_then_argmax():
    assert best_index([-3.0, -1.0, -2.0]) == 1


def test_given_tie_when_best_index_then_first():
    assert best_index([1.0, 1.0, 0.5]) == 0


def test_given_empty_when_best_index_then_raises():
    try:
        best_index([])
        assert False, "expected ValueError"
    except ValueError as e:
        assert "empty" in str(e)


def test_given_beats_both_when_decide_then_promote():
    stats = {
        "B4": {"mean_lp": -17.0, "mean_wall": 50.0},
        "GLOBAL": {"mean_lp": -16.5, "mean_wall": 60.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 55.0}
    assert decide_hdecp(s, stats).startswith("PROMOTE")


def test_given_leq_global_when_decide_then_kill():
    stats = {
        "B4": {"mean_lp": -17.0, "mean_wall": 50.0},
        "GLOBAL": {"mean_lp": -16.0, "mean_wall": 60.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 55.0}
    assert "≤ global gene" in decide_hdecp(s, stats)


def test_given_leq_b4_when_decide_then_kill():
    stats = {
        "B4": {"mean_lp": -16.0, "mean_wall": 50.0},
        "GLOBAL": {"mean_lp": -17.0, "mean_wall": 60.0},
    }
    s = {"mean_lp": -16.0, "mean_wall": 55.0}
    assert "≤ B4" in decide_hdecp(s, stats)
