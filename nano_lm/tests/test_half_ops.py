"""Contract: H-HALF dual gate vs H-PRE + fp16-wire helper."""

from __future__ import annotations

import torch

from half_ops import decide_hhalf, to_device_rec_half


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_ms_step": 10.0}
    stats = {"H-PRE": tip}
    assert decide_hhalf(
        {"mean_lp": -16.02, "mean_ms_step": 8.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hhalf(
        {"mean_lp": -16.2, "mean_ms_step": 7.0}, stats
    )
    assert "step-time" in decide_hhalf(
        {"mean_lp": -16.0, "mean_ms_step": 10.0}, stats
    )
    assert decide_hhalf({"mean_lp": -16.0, "mean_ms_step": 8.0}, {}).startswith(
        "needs H-PRE"
    )


def test_given_fp16_cache_when_to_device_half_then_logits_fp32() -> None:
    device = torch.device("cpu")
    rec = {
        "ids": torch.arange(4, dtype=torch.long).view(1, 4),
        "topk_idx": torch.zeros(1, 2, 3, dtype=torch.int32),
        "topk_val": torch.ones(1, 2, 3, dtype=torch.float16),
    }
    ids, logits = to_device_rec_half(
        rec, device=device, vocab_size=8, non_blocking=False
    )
    assert ids.dtype == torch.long
    assert logits.dtype == torch.float32
    assert logits.shape == (1, 2, 8)
