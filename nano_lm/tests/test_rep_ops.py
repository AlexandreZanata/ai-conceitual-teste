"""
Contract: H-REP repetition penalty + dual-gate decide vs B4.
"""

from __future__ import annotations

import torch

from rep_ops import PENALTIES, apply_rep_penalty, best_penalty_index, decide_hrep


def test_given_unit_penalty_when_apply_then_unchanged():
    logits = torch.tensor([[1.0, -2.0, 0.5]])
    prev = torch.tensor([[0, 1]])
    out = apply_rep_penalty(logits, prev, 1.0)
    assert torch.equal(out, logits)


def test_given_penalty_when_apply_then_seen_shrunk():
    logits = torch.tensor([[2.0, -2.0, 0.0]])
    prev = torch.tensor([[0, 1]])
    out = apply_rep_penalty(logits, prev, 2.0)
    assert float(out[0, 0]) == 1.0  # 2/2
    assert float(out[0, 1]) == -4.0  # -2*2
    assert float(out[0, 2]) == 0.0


def test_given_grid_when_best_then_argmax():
    assert best_penalty_index([-2.0, -1.0, -1.5]) == 1
    assert len(PENALTIES) >= 2


def test_given_dual_win_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_hrep({"mean_lp": -16.9, "mean_wall": 70.0}, stats).startswith(
        "PROMOTE"
    )


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert (
        decide_hrep({"mean_lp": -17.2, "mean_wall": 70.0}, stats)
        == "KILL (quality drop vs B4)"
    )
    assert (
        decide_hrep({"mean_lp": -16.9, "mean_wall": 90.0}, stats)
        == "KILL (no speedup vs B4)"
    )
