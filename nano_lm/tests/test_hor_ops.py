"""
Contract: H-HOR freezes tip n, clamps horizon≤2; dual gate vs H-POOL.
"""

from __future__ import annotations

import random

from hor_ops import (
    HORIZON_MAX,
    clamp_hor_gene,
    decide_hhor,
    mutate_hor_gene,
    seed_hor_from_tip,
)


def test_given_gene_when_clamp_then_n_frozen_and_horizon_capped():
    g = clamp_hor_gene(
        {
            "temperature": 0.8,
            "top_p": 0.9,
            "n": 6,
            "k": 2,
            "block": 1,
            "horizon": 4,
            "use_mae": False,
        },
        frozen_n=3,
    )
    assert g["n"] == 3
    assert g["horizon"] == HORIZON_MAX
    assert g["horizon"] <= 2


def test_given_mutate_when_run_then_n_frozen_horizon_capped():
    tip = {
        "temperature": 0.3,
        "top_p": 0.7,
        "n": 4,
        "k": 1,
        "block": 2,
        "horizon": 4,
        "use_mae": False,
    }
    for i in range(20):
        g = mutate_hor_gene(tip, frozen_n=4, rng=random.Random(i))
        assert g["n"] == 4
        assert g["horizon"] <= HORIZON_MAX


def test_given_tip_when_seed_then_n_matches_and_horizon_capped():
    tip = {
        "temperature": 0.2,
        "top_p": 0.5,
        "n": 5,
        "k": 2,
        "block": 1,
        "horizon": 3,
        "use_mae": False,
    }
    g = seed_hor_from_tip(tip, random.Random(2))
    assert g["n"] == 5
    assert g["horizon"] <= HORIZON_MAX


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_gflops": 12.0}
    stats = {"H-POOL": tip}
    assert decide_hhor({"mean_lp": -16.0, "mean_gflops": 10.0}, stats).startswith(
        "PROMOTE"
    )
    assert "quality" in decide_hhor({"mean_lp": -16.2, "mean_gflops": 8.0}, stats)
    assert "FLOP" in decide_hhor({"mean_lp": -15.9, "mean_gflops": 12.5}, stats)
