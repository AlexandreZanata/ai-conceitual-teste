"""
Contract: H-MID mid codebook + warm-start + decide vs H-EARLY.
"""

from __future__ import annotations

import random

from mid_ops import (
    MID_MIN_NEWS,
    clamp_mid_gene,
    decide_hmid,
    mutate_mid_gene,
    seed_mid_from_tip,
)


def test_given_tip12_when_clamp_then_mid8():
    g = clamp_mid_gene(
        {
            "min_new": 12,
            "patience": 2,
            "conf_threshold": 0.7,
            "n": 2,
            "temperature": 0.8,
            "top_p": 0.9,
        }
    )
    assert g["n"] == 1
    assert g["min_new"] == 8
    assert g["min_new"] in MID_MIN_NEWS


def test_given_tip_when_seed_then_n1():
    tip = {
        "min_new": 8,
        "patience": 2,
        "conf_threshold": 0.7,
        "n": 1,
        "temperature": 0.8,
        "top_p": 0.9,
    }
    g = seed_mid_from_tip(tip, random.Random(0))
    assert g["n"] == 1
    assert g["min_new"] in MID_MIN_NEWS


def test_given_mutate_when_run_then_valid():
    g = mutate_mid_gene(
        clamp_mid_gene(
            {
                "min_new": 4,
                "patience": 1,
                "conf_threshold": 0.6,
                "n": 1,
                "temperature": 0.5,
                "top_p": 0.8,
            }
        ),
        random.Random(2),
    )
    assert g["n"] == 1
    assert g["min_new"] in MID_MIN_NEWS


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_gflops": 9.0}
    stats = {"H-EARLY": tip}
    assert decide_hmid({"mean_lp": -16.0, "mean_gflops": 7.0}, stats).startswith(
        "PROMOTE"
    )
    assert "quality" in decide_hmid({"mean_lp": -16.2, "mean_gflops": 5.0}, stats)
    assert "FLOP" in decide_hmid({"mean_lp": -15.9, "mean_gflops": 9.5}, stats)
