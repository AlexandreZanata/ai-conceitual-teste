"""
Contract: Pareto front drops dominated points; knee near utopia; empty kills.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from pare_ops import decide_hpare, pareto_indices, pick_knee


def test_given_dominated_point_when_front_then_dropped():
    lps = [-10.0, -12.0, -11.0]
    walls = [50.0, 80.0, 40.0]
    # (-10,50) dominates (-12,80); (-11,40) is tradeoff with (-10,50)
    assert pareto_indices(lps, walls) == [0, 2]


def test_given_front_when_pick_knee_then_near_utopia():
    # Utopia = (max_lp=-10, min_wall=40). Midpoint (-11,50) is closest.
    lps = [-10.0, -14.0, -11.0]
    walls = [80.0, 40.0, 50.0]
    assert pick_knee(lps, walls) == 2


def test_given_empty_front_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.0, "mean_wall": 40.0, "front_n": 0.0}
    assert "empty Pareto front" in decide_hpare(s, stats)


def test_given_dominates_b4_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    s = {"mean_lp": -16.0, "mean_wall": 60.0, "front_n": 2.0}
    assert decide_hpare(s, stats).startswith("PROMOTE")
