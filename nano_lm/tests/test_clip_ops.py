"""
Contract: H-CLIP logit clip + clipped KD + decide vs B2.
"""

from __future__ import annotations

import torch

from clip_ops import DEFAULT_CLIP, clip_kd_loss, clip_logits, decide_hclip


def test_given_clip_when_apply_then_bounded():
    x = torch.tensor([[[-10.0, 3.0, 8.0]]])
    y = clip_logits(x, 5.0)
    assert float(y.min()) >= -5.0
    assert float(y.max()) <= 5.0
    assert torch.equal(clip_logits(x, 0.0), x)


def test_given_bad_clip_when_apply_then_raises():
    try:
        clip_logits(torch.zeros(1, 1, 2), -1.0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_logits_when_clip_kd_then_finite():
    s = torch.randn(2, 4, 16)
    t = torch.randn(2, 4, 16)
    ids = torch.randint(0, 16, (2, 4))
    loss = clip_kd_loss(
        s, t, ids, temperature=2.0, alpha=0.5, clip=DEFAULT_CLIP
    )
    assert torch.isfinite(loss)


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hclip({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hclip({"mean_lp": -17.0}, stats) == "KILL (≤ B2)"
