"""
Contract: H-ORAC teacher-oracle tip pick + dual-gate decide.
"""

from __future__ import annotations

from orac_ops import decide_horac, oracle_pick


def test_given_scores_when_oracle_then_argmax_tie_low():
    assert oracle_pick([-2.0, -1.0, -1.5]) == 1
    assert oracle_pick([-1.0, -1.0]) == 0


def test_given_empty_when_oracle_then_raises():
    try:
        oracle_pick([])
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_dual_win_when_decide_then_promote():
    stats = {
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0},
        "H-DECM": {"mean_lp": -16.3, "mean_wall": 200.0},
    }
    assert decide_horac({"mean_lp": -16.2, "mean_wall": 35.0}, stats).startswith(
        "PROMOTE"
    )


def test_given_wall_miss_when_decide_then_kill():
    stats = {
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0},
        "H-DECM": {"mean_lp": -16.3, "mean_wall": 200.0},
    }
    assert (
        decide_horac({"mean_lp": -16.2, "mean_wall": 50.0}, stats)
        == "KILL (no dual wall win)"
    )
    assert (
        decide_horac({"mean_lp": -16.5, "mean_wall": 30.0}, stats)
        == "KILL (≤ max tip quality)"
    )
