"""
Contract: H-EARS scheduled thr + decide vs H-EARLY.
"""

from __future__ import annotations

import random

from ears_ops import (
    PROMPT_REFS,
    clamp_ears_gene,
    decide_hears,
    mutate_ears_gene,
    random_ears_gene,
    scheduled_conf,
)


def test_given_raw_when_clamp_then_on_bounds():
    g = clamp_ears_gene(
        {
            "min_new": 8,
            "patience": 2,
            "conf_threshold": 0.8,
            "n": 1,
            "temperature": 0.8,
            "top_p": 0.9,
            "len_coef": 9.0,
            "budget_coef": -9.0,
            "prompt_ref": 99,
        }
    )
    assert -0.25 <= g["len_coef"] <= 0.25
    assert -0.35 <= g["budget_coef"] <= 0.15
    assert g["prompt_ref"] in PROMPT_REFS


def test_given_mutate_when_many_steps_then_valid():
    rng = random.Random(0)
    g = random_ears_gene(rng)
    for _ in range(25):
        g = mutate_ears_gene(g, rng)
        assert g["prompt_ref"] in PROMPT_REFS
        assert -0.25 <= g["len_coef"] <= 0.25


def test_given_budget_spent_when_schedule_then_thr_moves():
    base = 0.8
    early = scheduled_conf(
        base_thr=base,
        prompt_len=32,
        n_new=1,
        max_new=32,
        len_coef=0.0,
        budget_coef=-0.2,
        prompt_ref=32,
    )
    late = scheduled_conf(
        base_thr=base,
        prompt_len=32,
        n_new=31,
        max_new=32,
        len_coef=0.0,
        budget_coef=-0.2,
        prompt_ref=32,
    )
    assert late < early


def test_given_faster_quality_when_decide_then_promote():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.4, "mean_wall": 40.0}
    assert decide_hears(s, stats).startswith("PROMOTE")


def test_given_no_wall_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0}}
    s = {"mean_lp": -16.4, "mean_wall": 45.0}
    assert "no wall win" in decide_hears(s, stats)
