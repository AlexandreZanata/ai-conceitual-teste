"""Contract: H-TOP expand top-k + dual gate vs live STAG."""

from __future__ import annotations

import torch

from top_ops import decide_htop, expand_topk_logits


def test_given_topk_when_expand_then_scatter() -> None:
    idx = torch.tensor([[[1, 3]]], dtype=torch.int32)
    val = torch.tensor([[[2.0, 4.0]]])
    out = expand_topk_logits(idx, val, vocab_size=5, fill=-10.0)
    assert out.shape == (1, 1, 5)
    assert float(out[0, 0, 1]) == 2.0
    assert float(out[0, 0, 3]) == 4.0
    assert float(out[0, 0, 0]) == -10.0


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_ms_step": 40.0}
    stats = {"H-STAG": tip}
    assert decide_htop(
        {"mean_lp": -16.0, "mean_ms_step": 25.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_htop(
        {"mean_lp": -16.2, "mean_ms_step": 20.0}, stats
    )
    assert "step-time" in decide_htop(
        {"mean_lp": -15.9, "mean_ms_step": 40.0}, stats
    )
