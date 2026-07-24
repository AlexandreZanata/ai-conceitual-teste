"""
Contract: H-MINP min-p filter + dual-gate decide vs B4.
"""

from __future__ import annotations

import torch

from minp_ops import MIN_PS, apply_min_p, best_minp_index, decide_hminp


def test_given_zero_when_apply_then_identity():
    logits = torch.tensor([[2.0, 1.0, 0.0]])
    assert torch.equal(apply_min_p(logits, 0.0), logits)


def test_given_min_p_when_apply_then_low_mass_banned():
    # After softmax, max dominates; high min_p kills weak tokens.
    logits = torch.tensor([[10.0, 0.0, -5.0]])
    out = apply_min_p(logits, 0.5)
    assert float(out[0, 0]) == 10.0
    assert float(out[0, 2]) == float("-inf")


def test_given_bad_min_p_when_apply_then_raises():
    try:
        apply_min_p(torch.zeros(1, 2), 1.0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_grid_when_best_then_argmax():
    assert best_minp_index([-2.0, -1.0, -1.5]) == 1
    assert len(MIN_PS) >= 2


def test_given_dual_win_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_hminp(
        {"mean_lp": -16.9, "mean_wall": 70.0}, stats
    ).startswith("PROMOTE")


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert (
        decide_hminp({"mean_lp": -17.2, "mean_wall": 70.0}, stats)
        == "KILL (quality drop vs B4)"
    )
    assert (
        decide_hminp({"mean_lp": -16.9, "mean_wall": 90.0}, stats)
        == "KILL (no speedup vs B4)"
    )
