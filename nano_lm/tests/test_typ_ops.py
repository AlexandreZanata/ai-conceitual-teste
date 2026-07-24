"""
Contract: H-TYP typical filter + dual-gate decide vs B4.
"""

from __future__ import annotations

import torch

from typ_ops import TYP_MASSES, apply_typical, best_typ_index, decide_htyp


def test_given_unit_mass_when_apply_then_identity():
    logits = torch.tensor([[2.0, 1.0, 0.0]])
    assert torch.equal(apply_typical(logits, 1.0), logits)


def test_given_tight_mass_when_apply_then_some_banned():
    logits = torch.tensor([[5.0, 0.0, -2.0, -3.0]])
    out = apply_typical(logits, 0.7)
    assert (out == float("-inf")).any()
    assert not (out == float("-inf")).all()


def test_given_bad_mass_when_apply_then_raises():
    try:
        apply_typical(torch.zeros(1, 2), 0.0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_grid_when_best_then_argmax():
    assert best_typ_index([-2.0, -1.0, -1.5]) == 1
    assert len(TYP_MASSES) >= 2


def test_given_dual_win_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_htyp(
        {"mean_lp": -16.9, "mean_wall": 70.0}, stats
    ).startswith("PROMOTE")


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert (
        decide_htyp({"mean_lp": -17.2, "mean_wall": 70.0}, stats)
        == "KILL (quality drop vs B4)"
    )
    assert (
        decide_htyp({"mean_lp": -16.9, "mean_wall": 90.0}, stats)
        == "KILL (no speedup vs B4)"
    )
