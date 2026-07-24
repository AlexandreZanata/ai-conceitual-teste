"""
Contract: H-QG quality gate + min-GFLOPs pick + decide vs EARLY.
"""

from __future__ import annotations

import random

from qg_ops import (
    decide_hqg,
    passes_quality_gate,
    pick_min_gflops,
    seed_qg_from_tip,
)


def test_given_lp_when_gate_then_eps_holds():
    assert passes_quality_gate(-16.0, -16.0)
    assert passes_quality_gate(-16.04, -16.0)
    assert not passes_quality_gate(-16.06, -16.0)


def test_given_survivors_when_pick_then_min_gflops():
    # indices 0 fails gate; 1 and 2 pass; 2 has lower FLOPs
    assert pick_min_gflops([-17.0, -16.0, -15.9], [1.0, 5.0, 2.0], -16.0) == 2
    assert pick_min_gflops([-20.0, -19.0], [1.0, 2.0], -16.0) is None


def test_given_tip_when_seed_then_clamped_early_keys():
    tip = {
        "min_new": 8,
        "patience": 2,
        "conf_threshold": 0.8,
        "n": 1,
        "temperature": 0.5,
        "top_p": 0.9,
    }
    g = seed_qg_from_tip(tip, random.Random(0))
    assert set(g) == set(tip)


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_gflops": 12.0}
    stats = {"H-EARLY": tip}
    assert decide_hqg(
        {"mean_lp": -16.0, "mean_gflops": 10.0, "empty_rate": 0.0}, stats
    ).startswith("PROMOTE")
    assert "empty" in decide_hqg(
        {"mean_lp": -16.0, "mean_gflops": 10.0, "empty_rate": 1.0}, stats
    )
    assert "FLOP" in decide_hqg(
        {"mean_lp": -15.9, "mean_gflops": 12.5, "empty_rate": 0.0}, stats
    )
