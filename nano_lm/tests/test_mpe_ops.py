"""
Contract: H-MPE gene clamp/mutate + dual-gate decide vs H-MINP.
"""

from __future__ import annotations

import random

from minp_ops import MIN_PS
from mpe_ops import clamp_mpe_gene, decide_hmpe, mutate_mpe_gene, random_mpe_gene


def test_given_raw_when_clamp_then_on_codebook():
    g = clamp_mpe_gene({"min_p": 0.99, "temperature": 9.0, "top_p": 0.1})
    assert g["min_p"] in MIN_PS
    assert 0.2 <= g["temperature"] <= 1.5
    assert 0.5 <= g["top_p"] <= 1.0


def test_given_rng_when_random_mutate_then_clamped():
    rng = random.Random(0)
    g = random_mpe_gene(rng)
    m = mutate_mpe_gene(g, rng)
    assert m["min_p"] in MIN_PS


def test_given_dual_win_when_decide_then_promote():
    stats = {"H-MINP": {"mean_lp": -17.0, "mean_wall": 60.0}}
    assert decide_hmpe(
        {"mean_lp": -16.9, "mean_wall": 50.0}, stats
    ).startswith("PROMOTE")


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {"H-MINP": {"mean_lp": -17.0, "mean_wall": 60.0}}
    assert (
        decide_hmpe({"mean_lp": -17.2, "mean_wall": 50.0}, stats)
        == "KILL (quality drop vs H-MINP)"
    )
    assert (
        decide_hmpe({"mean_lp": -16.9, "mean_wall": 70.0}, stats)
        == "KILL (no speedup vs H-MINP)"
    )
