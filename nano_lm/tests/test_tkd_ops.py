"""
Contract: H-TKD top-k sparse KD loss + decide vs B2.
"""

from __future__ import annotations

import torch

from tkd_ops import DEFAULT_K, decide_htkd, topk_kd_loss


def test_given_logits_when_topk_kd_then_finite():
    s = torch.randn(2, 4, 20)
    t = torch.randn(2, 4, 20)
    ids = torch.randint(0, 20, (2, 4))
    loss = topk_kd_loss(s, t, ids, temperature=2.0, alpha=0.5, k=DEFAULT_K)
    assert torch.isfinite(loss)
    assert float(loss) > 0.0


def test_given_bad_k_when_topk_kd_then_raises():
    s = torch.randn(1, 2, 5)
    t = torch.randn(1, 2, 5)
    ids = torch.randint(0, 5, (1, 2))
    try:
        topk_kd_loss(s, t, ids, temperature=1.0, alpha=0.5, k=0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_htkd({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_htkd({"mean_lp": -17.0}, stats) == "KILL (≤ B2)"
