"""
Contract: H-TRIM freezes tip n; dual gate vs H-POOL.
"""

from __future__ import annotations

import random

from trim_ops import clamp_trim_gene, decide_htrim, mutate_trim_gene, seed_trim_from_tip


def test_given_gene_when_clamp_then_n_frozen():
    g = clamp_trim_gene(
        {
            "temperature": 0.8,
            "top_p": 0.9,
            "n": 6,
            "k": 2,
            "block": 1,
            "horizon": 2,
            "use_mae": False,
        },
        frozen_n=3,
    )
    assert g["n"] == 3


def test_given_mutate_when_run_then_n_unchanged():
    tip = {
        "temperature": 0.3,
        "top_p": 0.7,
        "n": 4,
        "k": 1,
        "block": 2,
        "horizon": 4,
        "use_mae": False,
    }
    g = mutate_trim_gene(tip, frozen_n=4, rng=random.Random(1))
    assert g["n"] == 4


def test_given_tip_when_seed_then_n_matches_tip():
    tip = {
        "temperature": 0.2,
        "top_p": 0.5,
        "n": 5,
        "k": 2,
        "block": 1,
        "horizon": 3,
        "use_mae": False,
    }
    g = seed_trim_from_tip(tip, random.Random(2))
    assert g["n"] == 5


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_gflops": 12.0}
    stats = {"H-POOL": tip}
    assert decide_htrim({"mean_lp": -16.0, "mean_gflops": 10.0}, stats).startswith(
        "PROMOTE"
    )
    assert "quality" in decide_htrim({"mean_lp": -16.2, "mean_gflops": 8.0}, stats)
    assert "FLOP" in decide_htrim({"mean_lp": -15.9, "mean_gflops": 12.5}, stats)
