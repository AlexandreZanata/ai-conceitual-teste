"""
Contract: H-ADV discriminator feats + mode collapse + decide vs B2.
"""

from __future__ import annotations

import torch

from adv_ops import (
    WeakDisc,
    decide_hadv,
    disc_bce,
    mode_collapsed,
    pred_entropy,
    soft_topk_feats,
)


def test_given_logits_when_feats_then_shape_k():
    logits = torch.randn(2, 5, 50)
    feats = soft_topk_feats(logits, k=8)
    assert feats.shape == (2, 8)
    assert float(feats.sum()) > 0.0


def test_given_disc_when_bce_then_real_lower_than_fake_on_ones():
    d = WeakDisc(k=4)
    feats = torch.ones(3, 4)
    with torch.no_grad():
        d.fc.weight.fill_(0.1)
        d.fc.bias.fill_(0.0)
    real = disc_bce(d(feats), real=True)
    fake = disc_bce(d(feats), real=False)
    assert float(real.detach()) < float(fake.detach())


def test_given_entropy_drop_when_mode_collapsed_then_true():
    assert mode_collapsed(4.0, 0.5, min_ratio=0.25)
    assert not mode_collapsed(4.0, 2.0, min_ratio=0.25)
    assert mode_collapsed(4.0, 0.0)


def test_given_uniform_logits_when_entropy_then_positive():
    logits = torch.zeros(1, 3, 10)
    assert pred_entropy(logits) > 1.0


def test_given_collapse_or_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert (
        decide_hadv({"mean_lp": -16.0, "mode_collapsed": 1.0}, stats)
        == "KILL (mode collapse)"
    )
    assert decide_hadv({"mean_lp": -17.1, "mode_collapsed": 0.0}, stats) == (
        "KILL (≤ B2)"
    )


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hadv({"mean_lp": -16.5, "mode_collapsed": 0.0}, stats).startswith(
        "PROMOTE"
    )
