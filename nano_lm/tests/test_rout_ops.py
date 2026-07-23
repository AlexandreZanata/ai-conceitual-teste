"""
Contract: H-ROUT confidence tip router + dual-gate decide.
"""

from __future__ import annotations

from rout_ops import DEFAULT_TAU, decide_hrout, route_tip


def test_given_high_conf_when_route_then_early():
    assert route_tip(0.9, tau=DEFAULT_TAU) == "early"
    assert route_tip(DEFAULT_TAU, tau=DEFAULT_TAU) == "early"


def test_given_low_conf_when_route_then_decm():
    assert route_tip(0.1, tau=DEFAULT_TAU) == "decm"


def test_given_bad_tau_when_route_then_raises():
    try:
        route_tip(0.5, tau=1.5)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_dual_win_when_decide_then_promote():
    stats = {
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0},
        "H-DECM": {"mean_lp": -16.3, "mean_wall": 200.0},
    }
    s = {"mean_lp": -16.25, "mean_wall": 35.0}
    assert decide_hrout(s, stats).startswith("PROMOTE")


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0},
        "H-DECM": {"mean_lp": -16.3, "mean_wall": 200.0},
    }
    assert (
        decide_hrout({"mean_lp": -16.5, "mean_wall": 35.0}, stats)
        == "KILL (≤ max tip quality)"
    )
    assert (
        decide_hrout({"mean_lp": -16.2, "mean_wall": 50.0}, stats)
        == "KILL (no dual wall win)"
    )
