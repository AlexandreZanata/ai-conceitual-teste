"""
Contract: H-JOINT gene clamp/mutate + free-lunch decide.
"""

from __future__ import annotations

import random

from joint_ops import (
    JOINT_LOS,
    JOINT_STAGES,
    clamp_joint_gene,
    decide_hjoint,
    mutate_joint_gene,
    random_joint_gene,
)


def test_given_raw_when_clamp_then_on_codebooks():
    g = clamp_joint_gene(
        {
            "seq_lo": 99,
            "n_stages": 1,
            "min_new": 4,
            "patience": 1,
            "conf_threshold": 0.7,
            "n": 1,
            "temperature": 0.8,
            "top_p": 0.9,
        }
    )
    assert g["seq_lo"] in JOINT_LOS
    assert g["n_stages"] in JOINT_STAGES


def test_given_rng_when_random_mutate_then_clamped():
    rng = random.Random(0)
    g = random_joint_gene(rng)
    m = mutate_joint_gene(g, rng)
    assert m["seq_lo"] in JOINT_LOS
    assert m["n_stages"] in JOINT_STAGES


def test_given_beats_both_when_decide_then_promote():
    stats = {
        "H-CURL": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-EARLY": {"mean_lp": -16.8, "mean_wall": 45.0},
    }
    assert decide_hjoint(
        {"mean_lp": -16.5, "mean_wall": 40.0}, stats
    ).startswith("PROMOTE")


def test_given_free_lunch_when_decide_then_kill():
    stats = {
        "H-CURL": {"mean_lp": -17.0, "mean_wall": 50.0},
        "H-EARLY": {"mean_lp": -16.5, "mean_wall": 45.0},
    }
    assert "≤ CURL" in decide_hjoint(
        {"mean_lp": -17.1, "mean_wall": 40.0}, stats
    )
    assert "≤ H-EARLY" in decide_hjoint(
        {"mean_lp": -16.6, "mean_wall": 40.0}, stats
    )
