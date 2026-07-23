"""
Contract: UCB1 prefers unpulled arms; H-BAND must beat max(H-DECK, H-CASC).
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from band_ops import decide_hband, ucb1_select


def test_given_unpulled_when_ucb1_then_prefer_unpulled():
    means = [1.0, 0.0, 0.5]
    counts = [3, 0, 1]
    assert ucb1_select(means, counts, total_pulls=4) == 1


def test_given_all_pulled_when_ucb1_then_pick_high_mean_or_explore():
    means = [0.0, 10.0, 1.0]
    counts = [100, 100, 100]
    assert ucb1_select(means, counts, total_pulls=300) == 1


def test_given_better_than_both_when_decide_then_promote():
    stats = {
        "H-DECK": {"mean_lp": -16.5},
        "H-CASC": {"mean_lp": -16.0},
    }
    s = {"mean_lp": -15.5}
    assert decide_hband(s, stats).startswith("PROMOTE")


def test_given_below_best_control_when_decide_then_kill():
    stats = {
        "H-DECK": {"mean_lp": -16.5},
        "H-CASC": {"mean_lp": -16.0},
    }
    s = {"mean_lp": -16.2}
    assert "≤ H-DECK / H-CASC" in decide_hband(s, stats)
