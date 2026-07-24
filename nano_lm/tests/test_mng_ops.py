"""
Contract: H-MNG dual gate vs H-MINP and H-NGRAM tips.
"""

from __future__ import annotations

from mng_ops import decide_hmng, tip_max_lp, tip_min_wall


def test_given_tips_when_max_min_then_correct():
    stats = {
        "H-MINP": {"mean_lp": -16.4, "mean_wall": 43.0},
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
    }
    assert tip_max_lp(stats) == -16.4
    assert tip_min_wall(stats) == 43.0


def test_given_dual_win_when_decide_then_promote():
    stats = {
        "H-MINP": {"mean_lp": -16.4, "mean_wall": 43.0},
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
    }
    assert decide_hmng(
        {"mean_lp": -16.35, "mean_wall": 40.0}, stats
    ) == "PROMOTE (dual win vs tips)"


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {
        "H-MINP": {"mean_lp": -16.4, "mean_wall": 43.0},
        "H-NGRAM": {"mean_lp": -16.5, "mean_wall": 44.0},
    }
    assert (
        decide_hmng({"mean_lp": -16.6, "mean_wall": 40.0}, stats)
        == "KILL (≤ max tip quality)"
    )
    assert (
        decide_hmng({"mean_lp": -16.35, "mean_wall": 43.5}, stats)
        == "KILL (no dual wall win)"
    )


def test_given_missing_tip_when_decide_then_needs():
    assert decide_hmng({"mean_lp": -11.0}, {}) == "needs H-MINP+H-NGRAM controls"
