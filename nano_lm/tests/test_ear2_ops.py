"""
Contract: H-EAR2 widened gene clamp + decide vs H-EARLY.
"""

from __future__ import annotations

import random

import torch

from ear2_ops import (
    CONF_METRICS,
    MAX_NEWS,
    MIN_NEWS2,
    clamp_ear2_gene,
    conf_score,
    decide_hear2,
    mutate_ear2_gene,
    random_ear2_gene,
)


def test_given_raw_when_clamp_then_on_codebooks():
    g = clamp_ear2_gene(
        {
            "min_new": 99,
            "max_new": 3,
            "patience": 9,
            "conf_threshold": 1.5,
            "n": 5,
            "temperature": 0.8,
            "top_p": 0.9,
            "conf_metric": "nope",
        }
    )
    assert g["min_new"] in MIN_NEWS2
    assert g["max_new"] in MAX_NEWS
    assert g["conf_metric"] in CONF_METRICS
    assert int(g["max_new"]) >= int(g["min_new"]) or g["max_new"] == MAX_NEWS[-1]


def test_given_mutate_when_many_steps_then_valid():
    rng = random.Random(0)
    g = random_ear2_gene(rng)
    for _ in range(25):
        g = mutate_ear2_gene(g, rng)
        assert g["min_new"] in MIN_NEWS2
        assert g["max_new"] in MAX_NEWS
        assert g["conf_metric"] in CONF_METRICS


def test_given_probs_when_conf_metrics_then_finite():
    probs = torch.softmax(torch.randn(2, 8), dim=-1)
    for m in CONF_METRICS:
        s = conf_score(probs, m)
        assert s.shape == (2,)
        assert torch.isfinite(s).all()


def test_given_faster_quality_when_decide_then_promote():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.4, "mean_wall": 40.0}
    assert decide_hear2(s, stats).startswith("PROMOTE")


def test_given_no_wall_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0}}
    s = {"mean_lp": -16.4, "mean_wall": 45.0}
    assert "no wall win" in decide_hear2(s, stats)
