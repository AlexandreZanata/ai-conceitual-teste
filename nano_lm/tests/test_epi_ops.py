"""
Contract: H-EPI context LR/mask helpers and decide vs B2.
"""

from __future__ import annotations

import torch

from epi_ops import (
    context_lr_scale,
    decide_hepi,
    mean_token_entropy,
    should_mask_embeds,
    zero_embed_grads,
)


def test_given_uniform_logits_when_entropy_then_positive():
    logits = torch.zeros(2, 3, 5)
    assert mean_token_entropy(logits) > 1.0


def test_given_entropy_bounds_when_scale_then_clamped_linear():
    assert context_lr_scale(0.0, ent_lo=0.0, ent_hi=2.0) == 0.5
    assert context_lr_scale(2.0, ent_lo=0.0, ent_hi=2.0) == 1.5
    mid = context_lr_scale(1.0, ent_lo=0.0, ent_hi=2.0)
    assert abs(mid - 1.0) < 1e-6


def test_given_easy_context_when_mask_then_true():
    assert should_mask_embeds(1.0, threshold=2.0)
    assert not should_mask_embeds(3.0, threshold=2.0)


def test_given_grads_when_zero_embed_then_cleared():
    class _W:
        def __init__(self):
            self.weight = torch.nn.Parameter(torch.ones(2, 2))
            self.weight.grad = torch.ones(2, 2)

        def parameters(self):
            yield self.weight

    class _T:
        def __init__(self):
            self.wte = _W()

    class _S:
        def __init__(self):
            self.transformer = _T()

    s = _S()
    zero_embed_grads(s)
    assert torch.count_nonzero(s.transformer.wte.weight.grad) == 0


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hepi({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hepi({"mean_lp": -17.1}, stats) == "KILL (≤ fixed LR / B2)"
