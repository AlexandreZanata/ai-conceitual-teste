"""
Contract: H-PROX decide vs H-POOL claim quality.
"""

from __future__ import annotations

from prox_ops import decide_hprox


def test_given_quality_hold_when_decide_then_promote():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 44.0}}
    s = {"mean_lp": -15.48, "mean_wall": 40.0}
    assert decide_hprox(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-POOL": {"mean_lp": -15.5, "mean_wall": 44.0}}
    s = {"mean_lp": -15.7, "mean_wall": 30.0}
    assert "quality drop" in decide_hprox(s, stats)


def test_given_missing_pool_when_decide_then_needs_control():
    assert "needs H-POOL" in decide_hprox({"mean_lp": -15.0}, {})
