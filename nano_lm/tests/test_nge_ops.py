"""
Contract: H-NGE gene clamp/mutate + dual-gate decide vs H-NGRAM.
"""

from __future__ import annotations

import random

from nge_ops import clamp_nge_gene, decide_hnge, mutate_nge_gene, random_nge_gene
from ngram_ops import NGRAM_SIZES


def test_given_raw_when_clamp_then_on_codebook():
    g = clamp_nge_gene({"ngram_size": 5, "temperature": 9.0, "top_p": 0.1})
    assert g["ngram_size"] in NGRAM_SIZES
    assert 0.2 <= g["temperature"] <= 1.5
    assert 0.5 <= g["top_p"] <= 1.0


def test_given_rng_when_random_mutate_then_clamped():
    rng = random.Random(0)
    g = random_nge_gene(rng)
    m = mutate_nge_gene(g, rng)
    assert m["ngram_size"] in NGRAM_SIZES


def test_given_dual_win_when_decide_then_promote():
    stats = {"H-NGRAM": {"mean_lp": -17.0, "mean_wall": 60.0}}
    assert decide_hnge(
        {"mean_lp": -16.9, "mean_wall": 50.0}, stats
    ).startswith("PROMOTE")


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {"H-NGRAM": {"mean_lp": -17.0, "mean_wall": 60.0}}
    assert (
        decide_hnge({"mean_lp": -17.2, "mean_wall": 50.0}, stats)
        == "KILL (quality drop vs H-NGRAM)"
    )
    assert (
        decide_hnge({"mean_lp": -16.9, "mean_wall": 70.0}, stats)
        == "KILL (no speedup vs H-NGRAM)"
    )
