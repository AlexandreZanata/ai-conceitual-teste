"""
Contract: H-NGRAM no-repeat ban + dual-gate decide vs B4.
"""

from __future__ import annotations

import torch

from ngram_ops import (
    NGRAM_SIZES,
    apply_ngram_ban,
    banned_next_tokens,
    best_ngram_index,
    decide_hngram,
)


def test_given_repeat_bigram_when_ban_then_token_blocked():
    # history: a b a → next ban b (would make a b a b with n=2 on "a"→"b")
    prev = [1, 2, 1]
    assert banned_next_tokens(prev, 2) == {2}
    assert banned_next_tokens(prev, 0) == set()
    assert banned_next_tokens([1], 2) == set()


def test_given_ban_when_apply_then_logit_neg_inf():
    logits = torch.tensor([[0.0, 1.0, 2.0]])
    prev = torch.tensor([[1, 2, 1]])
    out = apply_ngram_ban(logits, prev, 2)
    assert float(out[0, 2]) == float("-inf")
    assert float(out[0, 0]) == 0.0


def test_given_zero_size_when_apply_then_identity():
    logits = torch.tensor([[1.0, 2.0]])
    prev = torch.tensor([[0, 1]])
    assert torch.equal(apply_ngram_ban(logits, prev, 0), logits)


def test_given_bad_size_when_apply_then_raises():
    try:
        apply_ngram_ban(torch.zeros(1, 2), torch.zeros(1, 1, dtype=torch.long), -1)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_grid_when_best_then_argmax():
    assert best_ngram_index([-2.0, -1.0, -1.5]) == 1
    assert len(NGRAM_SIZES) >= 2


def test_given_dual_win_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert decide_hngram(
        {"mean_lp": -16.9, "mean_wall": 70.0}, stats
    ).startswith("PROMOTE")


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 80.0}}
    assert (
        decide_hngram({"mean_lp": -17.2, "mean_wall": 70.0}, stats)
        == "KILL (quality drop vs B4)"
    )
    assert (
        decide_hngram({"mean_lp": -16.9, "mean_wall": 90.0}, stats)
        == "KILL (no speedup vs B4)"
    )
