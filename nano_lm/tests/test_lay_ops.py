"""
Contract: H-LAY clamps max_skip/lay_conf; dual gate vs H-EARLY.
"""

from __future__ import annotations

import random

from lay_ops import (
    MAX_SKIPS,
    clamp_lay_gene,
    decide_hlay,
    mutate_lay_gene,
    scale_flops_by_layers,
)


def test_given_raw_when_clamp_then_on_codebooks():
    g = clamp_lay_gene({"max_skip": 9, "lay_conf": 1.5})
    assert g["max_skip"] in MAX_SKIPS
    assert 0.5 <= float(g["lay_conf"]) <= 0.99


def test_given_mutate_when_many_then_stays_valid():
    rng = random.Random(0)
    g = clamp_lay_gene({"max_skip": 1, "lay_conf": 0.7})
    for _ in range(30):
        g = mutate_lay_gene(g, rng)
        assert g["max_skip"] in MAX_SKIPS
        assert 0.5 <= float(g["lay_conf"]) <= 0.99


def test_given_half_layers_when_scale_then_half_flops():
    assert scale_flops_by_layers(
        100.0, layer_evals=10, token_evals=10, n_layers=2
    ) == 50.0


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_wall": 80.0, "mean_gflops": 12.0}
    stats = {"H-EARLY": tip}
    assert decide_hlay(
        {"mean_lp": -16.0, "mean_wall": 70.0, "mean_gflops": 12.0}, stats
    ).startswith("PROMOTE")
    assert decide_hlay(
        {"mean_lp": -16.0, "mean_wall": 90.0, "mean_gflops": 10.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hlay(
        {"mean_lp": -16.2, "mean_wall": 50.0, "mean_gflops": 8.0}, stats
    )
    assert "wall/GFLOPs" in decide_hlay(
        {"mean_lp": -15.9, "mean_wall": 90.0, "mean_gflops": 12.5}, stats
    )
