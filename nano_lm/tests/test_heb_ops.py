"""
Contract: H-HEB Hebbian delta + diverge + decide vs B2.
"""

from __future__ import annotations

import torch

from heb_ops import apply_hebbian, decide_hheb, diverged, hebbian_delta


def test_given_pre_post_when_delta_then_outer_mean_shape():
    pre = torch.ones(2, 3)
    post = torch.tensor([[1.0, 0.0], [1.0, 0.0]])
    d = hebbian_delta(pre, post, eta=2.0)
    assert d.shape == (2, 3)
    # Two samples, eta=2 → scale 1; outer gives 2 on first out-row.
    assert torch.allclose(d[0], torch.full((3,), 2.0))
    assert torch.allclose(d[1], torch.zeros(3))
    half = hebbian_delta(pre, post, eta=1.0)
    assert torch.allclose(half, d * 0.5)


def test_given_weight_when_apply_then_increases():
    w = torch.zeros(2, 3)
    apply_hebbian(w, torch.ones(4, 3), torch.ones(4, 2), eta=1.0)
    assert float(w.mean()) > 0.0


def test_given_spike_when_diverged_then_true():
    assert diverged([1.0, 2.0, 20.0])
    assert not diverged([1.0, 1.1, 1.2])
    assert diverged([1.0, float("nan")])


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hheb({"mean_lp": -16.5, "diverged": 0.0}, stats).startswith(
        "PROMOTE"
    )


def test_given_le_b2_or_diverge_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hheb({"mean_lp": -17.1, "diverged": 0.0}, stats) == "KILL (≤ B2)"
    assert (
        decide_hheb({"mean_lp": -16.0, "diverged": 1.0}, stats) == "KILL (diverged)"
    )
