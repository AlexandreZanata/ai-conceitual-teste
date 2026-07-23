"""
Contract: H-DEB teacher pick + soft KL + decide vs B2.
"""

from __future__ import annotations

import torch

from deb_ops import decide_hdeb, peer_kl, soft_kl, teacher_pick


def test_given_closer_student_when_soft_kl_then_lower():
    tea = torch.zeros(1, 3, 5)
    tea[0, :, 0] = 5.0
    close = tea.clone()
    far = torch.zeros_like(tea)
    far[0, :, 4] = 5.0
    assert float(soft_kl(close, tea)) < float(soft_kl(far, tea))


def test_given_scores_when_pick_then_lower_wins_tie_a():
    assert teacher_pick(1.0, 2.0) == 0
    assert teacher_pick(2.0, 1.0) == 1
    assert teacher_pick(1.0, 1.0) == 0


def test_given_peer_when_kl_then_finite():
    a = torch.randn(1, 4, 8)
    b = torch.randn(1, 4, 8)
    v = peer_kl(a, b.detach())
    assert torch.isfinite(v)


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hdeb({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hdeb({"mean_lp": -17.0}, stats) == "KILL (≤ B2)"
    assert decide_hdeb({"mean_lp": -17.1}, stats) == "KILL (≤ B2)"
