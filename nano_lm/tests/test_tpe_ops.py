"""
Contract: H-TPE gene clamp/mutate + dual-gate decide vs H-TYP.
"""

from __future__ import annotations

import random

from tpe_ops import clamp_tpe_gene, decide_htpe, mutate_tpe_gene, random_tpe_gene
from typ_ops import TYP_MASSES


def test_given_raw_when_clamp_then_on_codebook():
    g = clamp_tpe_gene({"typ_mass": 0.05, "temperature": 9.0, "top_p": 0.1})
    assert g["typ_mass"] in TYP_MASSES
    assert 0.2 <= g["temperature"] <= 1.5
    assert 0.5 <= g["top_p"] <= 1.0


def test_given_rng_when_random_mutate_then_clamped():
    rng = random.Random(0)
    g = random_tpe_gene(rng)
    m = mutate_tpe_gene(g, rng)
    assert m["typ_mass"] in TYP_MASSES


def test_given_dual_win_when_decide_then_promote():
    stats = {"H-TYP": {"mean_lp": -17.0, "mean_wall": 60.0}}
    assert decide_htpe(
        {"mean_lp": -16.9, "mean_wall": 50.0}, stats
    ).startswith("PROMOTE")


def test_given_quality_or_wall_miss_when_decide_then_kill():
    stats = {"H-TYP": {"mean_lp": -17.0, "mean_wall": 60.0}}
    assert (
        decide_htpe({"mean_lp": -17.2, "mean_wall": 50.0}, stats)
        == "KILL (quality drop vs H-TYP)"
    )
    assert (
        decide_htpe({"mean_lp": -16.9, "mean_wall": 70.0}, stats)
        == "KILL (no speedup vs H-TYP)"
    )
