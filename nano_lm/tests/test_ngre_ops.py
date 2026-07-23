"""
Contract: H-NGRE dual gate vs H-NGRAM and H-EARLY tips.
"""

from __future__ import annotations

from ngre_ops import decide_hngre, tip_max_lp, tip_min_wall


def test_given_tips_when_max_min_then_correct():
    stats = {
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
        "H-EARLY": {"mean_lp": -16.6, "mean_wall": 40.0},
    }
    assert tip_max_lp(stats) == -16.5
    assert tip_min_wall(stats) == 40.0


def test_given_dual_win_when_decide_then_promote():
    stats = {
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
        "H-EARLY": {"mean_lp": -16.6, "mean_wall": 40.0},
    }
    assert decide_hngre(
        {"mean_lp": -16.45, "mean_wall": 35.0}, stats
    ) == "PROMOTE (dual win vs tips)"


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
        "H-EARLY": {"mean_lp": -16.6, "mean_wall": 40.0},
    }
    assert (
        decide_hngre({"mean_lp": -16.7, "mean_wall": 35.0}, stats)
        == "KILL (≤ max tip quality)"
    )
    assert (
        decide_hngre({"mean_lp": -16.45, "mean_wall": 42.0}, stats)
        == "KILL (no dual wall win)"
    )


def test_given_missing_tip_when_decide_then_needs():
    assert decide_hngre({"mean_lp": -11.0}, {}) == "needs H-NGRAM+H-EARLY controls"
