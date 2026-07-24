"""Contract: H-TOPK slice + dual gate vs tip k=64."""

from __future__ import annotations

import torch

from top_ops import DEFAULT_TOP_K
from topk_ops import (
    SMOKE_BEST_K,
    TIP_TOP_K,
    TOPK_SWEEP,
    beats_tip_k,
    decide_htopk,
    slice_topk_records,
)


def test_given_sweep_when_defined_then_includes_tip() -> None:
    assert TIP_TOP_K == DEFAULT_TOP_K == 64
    assert TIP_TOP_K in TOPK_SWEEP
    assert TOPK_SWEEP == (16, 32, 64, 128)
    assert SMOKE_BEST_K in TOPK_SWEEP and SMOKE_BEST_K != TIP_TOP_K


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    from hold_ops import assert_disjoint, load_prompt_ids
    from run_formal_htopk import formal_cfg

    c = formal_cfg()
    assert "eval_prompts" in str(c["prompts"])
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert int(c["steps_kd"]) >= 120
    assert c["seeds"] == [0, 1, 2]


def test_given_max_cache_when_slice_then_exact_width() -> None:
    rec = {
        "ids": torch.zeros(1, 2, dtype=torch.long),
        "topk_idx": torch.arange(8, dtype=torch.int32).view(1, 1, 8),
        "topk_val": torch.linspace(8.0, 1.0, 8).view(1, 1, 8),
    }
    sliced = slice_topk_records([rec], 3)[0]
    assert sliced["topk_idx"].shape[-1] == 3
    assert sliced["topk_val"].tolist() == [[[8.0, 7.0, 6.0]]]


def test_given_oversized_k_when_slice_then_raises() -> None:
    rec = {
        "ids": torch.zeros(1, 1, dtype=torch.long),
        "topk_idx": torch.zeros(1, 1, 2, dtype=torch.int32),
        "topk_val": torch.zeros(1, 1, 2),
    }
    try:
        slice_topk_records([rec], 3)
        raise AssertionError("expected ValueError")
    except ValueError as exc:
        assert "exceeds" in str(exc)


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_ms_step": 10.0}
    by_k = {
        64: tip,
        16: {"mean_lp": -16.0, "mean_ms_step": 8.0},
        32: {"mean_lp": -16.2, "mean_ms_step": 7.0},
        128: {"mean_lp": -15.9, "mean_ms_step": 11.0},
    }
    assert decide_htopk(by_k).startswith("PROMOTE (best k=16")
    assert beats_tip_k(by_k[16], tip)
    assert not beats_tip_k(by_k[32], tip)
    assert not beats_tip_k(by_k[128], tip)
    kill = {64: tip, 16: {"mean_lp": -16.2, "mean_ms_step": 8.0}}
    assert decide_htopk(kill).startswith("KILL")
