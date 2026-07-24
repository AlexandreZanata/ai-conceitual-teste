"""Contract: H-REP penalty/ngram helpers + quality@wall gate vs EARLY."""

from __future__ import annotations

import torch

from rep_ops import (
    apply_repetition_penalty,
    ban_ngram_logits,
    clamp_rep_gene,
    decide_hrep,
)


def test_given_seen_token_when_penalty_then_downweight() -> None:
    logits = torch.tensor([[2.0, -2.0, 0.5]])
    ids = torch.tensor([[0, 1]])
    out = apply_repetition_penalty(logits, ids, penalty=2.0)
    assert float(out[0, 0]) == 1.0  # 2/2
    assert float(out[0, 1]) == -4.0  # -2*2
    assert float(out[0, 2]) == 0.5


def test_given_ngram_when_ban_then_block_repeat() -> None:
    logits = torch.zeros(1, 5)
    ids = torch.tensor([[1, 2, 1]])  # seen (1,2),(2,1); prefix (1,) bans 2
    out = ban_ngram_logits(logits, ids, ngram=2)
    assert float(out[0, 2]) == float("-inf")
    assert float(out[0, 3]) == 0.0


def test_given_tip_when_clamp_then_codebook() -> None:
    tip = {"n": 1, "temperature": 0.8, "top_p": 0.9, "min_new": 8, "patience": 2,
           "conf_threshold": 0.7}
    g = clamp_rep_gene({"rep_penalty": 1.17, "no_repeat_ngram": 2}, tip)
    assert g["rep_penalty"] == 1.2
    assert g["no_repeat_ngram"] == 2
    assert g["min_new"] == 8


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_wall": 70.0}
    stats = {"H-EARLY": tip}
    assert decide_hrep(
        {"mean_lp": -15.5, "mean_wall": 65.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hrep(
        {"mean_lp": -16.0, "mean_wall": 50.0}, stats
    )
    assert "wall" in decide_hrep(
        {"mean_lp": -15.5, "mean_wall": 80.0}, stats
    )
