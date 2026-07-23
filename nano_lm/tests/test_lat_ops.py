"""
Contract: latency-aware score decreases with wall; H-LAT gate needs quality+speed.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lat_ops import decide_hlat, latency_aware_score


def test_given_same_lp_when_higher_wall_then_score_drops():
    a = latency_aware_score(-10.0, 10.0, 0.2)
    b = latency_aware_score(-10.0, 100.0, 0.2)
    assert a > b


def test_given_lam_zero_when_scoring_then_equals_lp():
    assert latency_aware_score(-12.5, 999.0, 0.0) == -12.5


def test_given_better_and_faster_when_decide_then_promote():
    stats = {
        "B4": {"mean_lp": -17.0, "mean_wall": 100.0},
        "H-DEC": {"mean_lp": -16.9, "mean_wall": 120.0},
    }
    s = {"mean_lp": -16.95, "mean_wall": 80.0}
    assert decide_hlat(s, stats).startswith("PROMOTE")


def test_given_no_speedup_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.5, "mean_wall": 50.0}
    assert "no speedup" in decide_hlat(s, stats)
