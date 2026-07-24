"""Contract: H-PIN pin_records + dual gate vs H-TOP."""

from __future__ import annotations

import torch

from pin_ops import decide_hpin, pin_records


def test_given_cpu_cache_when_pin_then_pinned_contiguous() -> None:
    rec = {
        "ids": torch.arange(4, dtype=torch.long).view(1, 4),
        "topk_idx": torch.zeros(1, 2, 3, dtype=torch.int32),
        "topk_val": torch.ones(1, 2, 3, dtype=torch.float16),
    }
    pinned = pin_records([rec])[0]
    assert pinned["ids"].is_pinned()
    assert pinned["topk_idx"].is_pinned()
    assert pinned["topk_val"].is_pinned()
    assert pinned["ids"].is_contiguous()


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_ms_step": 10.0}
    stats = {"H-TOP": tip}
    assert decide_hpin(
        {"mean_lp": -16.0, "mean_ms_step": 8.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hpin(
        {"mean_lp": -16.2, "mean_ms_step": 7.0}, stats
    )
    assert "step-time" in decide_hpin(
        {"mean_lp": -15.9, "mean_ms_step": 10.0}, stats
    )


def test_given_missing_tip_when_decide_then_needs() -> None:
    assert decide_hpin({"mean_lp": -1.0, "mean_ms_step": 1.0}, {}).startswith(
        "needs H-TOP"
    )


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    from hold_ops import assert_disjoint, load_prompt_ids
    from run_formal_hpin import formal_cfg

    c = formal_cfg()
    assert "eval_prompts" in str(c["prompts"])
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert int(c["steps_kd"]) >= 120
    assert c["seeds"] == [0, 1, 2]
