"""
Contract: H-LOT magnitude masks, rewind, and decide vs B2.
"""

from __future__ import annotations

import torch
import torch.nn as nn

from lot_ops import (
    apply_weight_masks,
    build_magnitude_masks,
    collect_linear_inits,
    decide_hlot,
    magnitude_keep_mask,
    mask_keep_frac,
    rewind_linears,
)


def test_given_keep_half_when_mask_then_half_ones():
    w = torch.tensor([0.1, 0.9, 0.2, 0.8])
    m = magnitude_keep_mask(w, 0.5)
    assert int(m.sum().item()) == 2
    assert float(m[1]) == 1.0 and float(m[3]) == 1.0


def test_given_model_when_rewind_then_sparse_init():
    lin = nn.Linear(2, 2, bias=False)
    with torch.no_grad():
        lin.weight.copy_(torch.tensor([[1.0, 2.0], [3.0, 4.0]]))
    model = nn.Sequential(lin)
    # named_modules: '' and '0'
    inits = collect_linear_inits(model)
    masks = {"0": torch.tensor([[1.0, 0.0], [0.0, 1.0]])}
    with torch.no_grad():
        lin.weight.fill_(9.0)
    rewind_linears(model, inits, masks)
    assert torch.allclose(lin.weight, torch.tensor([[1.0, 0.0], [0.0, 4.0]]))


def test_given_masks_when_apply_then_zeros_pruned():
    lin = nn.Linear(2, 1, bias=False)
    with torch.no_grad():
        lin.weight.copy_(torch.ones(1, 2))
    model = nn.Sequential(lin)
    apply_weight_masks(model, {"0": torch.tensor([[1.0, 0.0]])})
    assert float(lin.weight.detach()[0, 1]) == 0.0


def test_given_keep_frac_when_build_then_reported():
    lin = nn.Linear(4, 1, bias=False)
    model = nn.Sequential(lin)
    masks = build_magnitude_masks(model, 0.5)
    assert 0.4 <= mask_keep_frac(masks) <= 0.6


def test_given_cliff_when_decide_then_kill_cliff():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hlot({"mean_lp": -17.6}, stats) == "KILL (quality cliff)"
    assert decide_hlot({"mean_lp": -17.1}, stats) == "KILL (≤ B2)"
    assert decide_hlot({"mean_lp": -16.5}, stats).startswith("PROMOTE")
