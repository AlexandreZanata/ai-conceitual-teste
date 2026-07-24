"""Contract: H-POOLB throughput dual gate vs serial POOL."""

from __future__ import annotations

from poolb_ops import decide_hpoolb
from poolb_score import throughput_gene


def test_given_pool_tip_when_throughput_gene_then_n1_greedy() -> None:
    tip = {
        "temperature": 0.8,
        "top_p": 0.9,
        "n": 3,
        "k": 2,
        "block": 2,
        "horizon": 2,
        "use_mae": True,
    }
    g = throughput_gene(tip)
    assert g["n"] == 1
    assert g["temperature"] == 1e-6
    assert g["use_mae"] is False
    assert abs(float(g["top_p"]) - 0.9) < 1e-9


def test_given_throughput_gene_when_policy_then_keeps_near_greedy() -> None:
    from poolb_score import _policy

    tip = throughput_gene(
        {
            "temperature": 0.8,
            "top_p": 0.7,
            "n": 4,
            "k": 1,
            "block": 1,
            "horizon": 1,
            "use_mae": False,
        }
    )
    g = _policy(tip)
    assert g["temperature"] == 1e-6
    assert g["n"] == 1


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -16.0, "mean_tps": 100.0}
    stats = {"H-POOL": tip}
    assert decide_hpoolb(
        {"mean_lp": -16.02, "mean_tps": 150.0}, stats
    ).startswith("PROMOTE")
    assert "lp change" in decide_hpoolb(
        {"mean_lp": -16.2, "mean_tps": 200.0}, stats
    )
    assert "tok/s" in decide_hpoolb(
        {"mean_lp": -16.0, "mean_tps": 90.0}, stats
    )


def test_given_missing_tip_when_decide_then_needs() -> None:
    assert decide_hpoolb({"mean_lp": -1.0, "mean_tps": 1.0}, {}).startswith(
        "needs H-POOL"
    )


def test_given_formal_cfg_when_load_then_fit_neq_eval() -> None:
    from hold_ops import assert_disjoint, load_prompt_ids
    from run_formal_hpoolb import formal_cfg

    c = formal_cfg()
    assert "eval_prompts" in str(c["prompts"])
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert c["seeds"] == [0, 1, 2]
