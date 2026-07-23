"""
Contract: H-NGDM dual gate vs H-NGRAM and H-DECM tips.
"""

from __future__ import annotations

from ngdm_ops import decide_hngdm, tip_max_lp, tip_min_wall


def test_given_tips_when_max_min_then_correct():
    stats = {
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
        "H-DECM": {"mean_lp": -15.0, "mean_wall": 90.0},
    }
    assert tip_max_lp(stats) == -15.0
    assert tip_min_wall(stats) == 44.0


def test_given_dual_win_when_decide_then_promote():
    stats = {
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
        "H-DECM": {"mean_lp": -15.0, "mean_wall": 90.0},
    }
    assert decide_hngdm(
        {"mean_lp": -14.9, "mean_wall": 40.0}, stats
    ) == "PROMOTE (dual win vs tips)"


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
        "H-DECM": {"mean_lp": -15.0, "mean_wall": 90.0},
    }
    assert (
        decide_hngdm({"mean_lp": -15.2, "mean_wall": 40.0}, stats)
        == "KILL (≤ max tip quality)"
    )
    assert (
        decide_hngdm({"mean_lp": -14.9, "mean_wall": 50.0}, stats)
        == "KILL (no dual wall win)"
    )


def test_given_missing_tip_when_decide_then_needs():
    assert decide_hngdm({"mean_lp": -11.0}, {}) == "needs H-NGRAM+H-DECM controls"
