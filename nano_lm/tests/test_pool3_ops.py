"""
Contract: H-POOL3 n≤3 clamp + decide vs H-POOL tip.
"""

from __future__ import annotations

import random

from pool3_ops import (
    N_MAX,
    clamp_pool3_gene,
    decide_hpool3,
    mutate_pool3_gene,
    seed_pool3_from_tip,
)


def test_given_n4_when_clamp_then_n_max():
    g = clamp_pool3_gene(
        {
            "temperature": 0.8,
            "top_p": 0.9,
            "n": 4,
            "k": 2,
            "block": 1,
            "horizon": 2,
            "use_mae": False,
        }
    )
    assert g["n"] == N_MAX
    assert N_MAX == 3


def test_given_tip_when_seed_then_n_le_max():
    tip = {
        "temperature": 0.3,
        "top_p": 0.7,
        "n": 6,
        "k": 1,
        "block": 2,
        "horizon": 4,
        "use_mae": False,
    }
    g = seed_pool3_from_tip(tip, random.Random(0))
    assert 1 <= g["n"] <= N_MAX


def test_given_mutate_when_run_then_n_bounded():
    g = mutate_pool3_gene(
        clamp_pool3_gene(
            {
                "temperature": 0.5,
                "top_p": 0.8,
                "n": 3,
                "k": 1,
                "block": 1,
                "horizon": 1,
                "use_mae": False,
            }
        ),
        random.Random(1),
    )
    assert 1 <= g["n"] <= N_MAX


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_gflops": 12.0}
    stats = {"H-POOL": tip}
    assert decide_hpool3({"mean_lp": -16.0, "mean_gflops": 10.0}, stats).startswith(
        "PROMOTE"
    )
    assert "quality" in decide_hpool3({"mean_lp": -16.2, "mean_gflops": 8.0}, stats)
    assert "FLOP" in decide_hpool3({"mean_lp": -15.9, "mean_gflops": 12.5}, stats)
