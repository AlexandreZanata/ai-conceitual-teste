"""
Contract: H-LS label-smoothed KD + decide vs B2.
"""

from __future__ import annotations

import torch

from ls_ops import DEFAULT_EPS, decide_hls, smooth_kd_loss


def test_given_logits_when_smooth_kd_then_finite():
    s = torch.randn(2, 3, 10)
    t = torch.randn(2, 3, 10)
    ids = torch.randint(0, 10, (2, 3))
    loss = smooth_kd_loss(
        s, t, ids, temperature=2.0, alpha=0.5, eps=DEFAULT_EPS
    )
    assert torch.isfinite(loss)
    assert float(loss) > 0.0


def test_given_bad_eps_when_smooth_kd_then_raises():
    s = torch.randn(1, 2, 4)
    t = torch.randn(1, 2, 4)
    ids = torch.randint(0, 4, (1, 2))
    try:
        smooth_kd_loss(s, t, ids, temperature=1.0, alpha=0.5, eps=1.0)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hls({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hls({"mean_lp": -17.0}, stats) == "KILL (≤ B2)"
