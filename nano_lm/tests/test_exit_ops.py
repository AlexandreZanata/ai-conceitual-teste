"""
Contract: H-EXIT gene clamp (min_new↓, n=1) + decide vs H-EARLY.
"""

from __future__ import annotations

from exit_ops import (
    EXIT_MIN_NEWS,
    clamp_exit_gene,
    decide_hexit,
    mutate_exit_gene,
    random_exit_gene,
)


def test_given_raw_when_clamp_then_n1_and_exit_mins():
    g = clamp_exit_gene(
        {
            "min_new": 3,
            "patience": 2,
            "conf_threshold": 0.7,
            "n": 2,
            "temperature": 0.8,
            "top_p": 0.9,
        }
    )
    assert g["n"] == 1
    assert g["min_new"] in EXIT_MIN_NEWS


def test_given_rng_when_random_then_valid():
    import random

    g = random_exit_gene(random.Random(0))
    assert g["n"] == 1
    assert g["min_new"] in EXIT_MIN_NEWS


def test_given_mutate_when_run_then_stays_valid():
    import random

    rng = random.Random(1)
    g = mutate_exit_gene(random_exit_gene(rng), rng)
    assert g["n"] == 1
    assert g["min_new"] in EXIT_MIN_NEWS


def test_given_flop_win_when_decide_then_promote():
    stats = {"H-EARLY": {"mean_lp": -16.0, "mean_gflops": 9.0}}
    assert decide_hexit(
        {"mean_lp": -16.0, "mean_gflops": 7.0}, stats
    ).startswith("PROMOTE")


def test_given_no_flop_win_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.0, "mean_gflops": 9.0}}
    assert "FLOP" in decide_hexit({"mean_lp": -15.9, "mean_gflops": 9.0}, stats)
