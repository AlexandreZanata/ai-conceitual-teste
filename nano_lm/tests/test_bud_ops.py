"""
Contract: H-BUD gene clamp + dominate decide vs H-EARLY.
"""

from __future__ import annotations

import random

from bud_ops import (
    BUD_MAX_NEWS,
    clamp_bud_gene,
    decide_hbud,
    from_early_tip,
    mutate_bud_gene,
    random_bud_gene,
)
from early_ops import MIN_NEWS


def test_given_raw_when_clamp_then_max_new_on_codebook():
    g = clamp_bud_gene(
        {
            "min_new": 8,
            "max_new": 99,
            "patience": 2,
            "conf_threshold": 0.8,
            "n": 1,
            "temperature": 0.9,
            "top_p": 0.9,
        }
    )
    assert g["max_new"] in BUD_MAX_NEWS
    assert g["min_new"] in MIN_NEWS
    assert int(g["max_new"]) >= int(g["min_new"])


def test_given_early_tip_when_from_tip_then_has_max_new():
    tip = {
        "min_new": 8,
        "patience": 2,
        "conf_threshold": 0.7,
        "n": 1,
        "temperature": 0.8,
        "top_p": 0.9,
    }
    g = from_early_tip(tip, max_new=12)
    assert g["max_new"] == 12


def test_given_mutate_when_many_steps_then_valid():
    rng = random.Random(1)
    g = random_bud_gene(rng)
    for _ in range(20):
        g = mutate_bud_gene(g, rng)
        assert g["max_new"] in BUD_MAX_NEWS


def test_given_wall_win_quality_when_decide_then_promote():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.45, "mean_wall": 40.0}
    assert decide_hbud(s, stats).startswith("PROMOTE")


def test_given_dominated_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0}}
    s = {"mean_lp": -16.6, "mean_wall": 45.0}
    assert "KILL" in decide_hbud(s, stats)
