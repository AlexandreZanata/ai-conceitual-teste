"""
Contract: Pareto dominate needs both axes; H-DECKL kills when dominated.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from deckl_ops import decide_hdeckl, dominates_lp_wall


def test_given_better_lp_and_wall_when_dominates_then_true():
    assert dominates_lp_wall(-10.0, 50.0, -12.0, 80.0) is True


def test_given_tradeoff_when_dominates_then_false():
    assert dominates_lp_wall(-10.0, 100.0, -12.0, 50.0) is False


def test_given_dominates_b4_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    s = {"mean_lp": -16.0, "mean_wall": 60.0}
    assert decide_hdeckl(s, stats).startswith("PROMOTE")


def test_given_dominated_by_b4_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -16.0, "mean_wall": 50.0}}
    s = {"mean_lp": -17.0, "mean_wall": 80.0}
    assert "dominated on Pareto by B4" in decide_hdeckl(s, stats)
