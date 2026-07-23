"""
Contract: H-HOP Hopfield retrieve/mix/store and decide vs B2.
"""

from __future__ import annotations

import torch

from hop_ops import decide_hhop, hopfield_retrieve, mix_hidden, push_patterns


def test_given_matching_pattern_when_retrieve_then_near_pattern():
    patterns = torch.tensor([[1.0, 0.0], [0.0, 1.0]])
    query = torch.tensor([[0.9, 0.1]])
    out = hopfield_retrieve(query, patterns, beta=20.0)
    assert out.shape == query.shape
    assert float(out[0, 0]) > float(out[0, 1])


def test_given_alpha_when_mix_then_scaled_sum():
    h = torch.ones(2, 3)
    r = torch.full((2, 3), 2.0)
    m = mix_hidden(h, r, alpha=0.5)
    assert torch.allclose(m, torch.full((2, 3), 2.0))


def test_given_vectors_when_push_then_bank_updates():
    bank = torch.zeros(3, 2)
    cur = push_patterns(bank, torch.tensor([[1.0, 2.0], [3.0, 4.0]]), cursor=0)
    assert cur == 2
    assert torch.allclose(bank[0], torch.tensor([1.0, 2.0]))
    assert torch.allclose(bank[1], torch.tensor([3.0, 4.0]))


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hhop({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hhop({"mean_lp": -17.1}, stats) == "KILL (no gain vs B2)"
