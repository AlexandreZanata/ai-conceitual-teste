"""
Contract: H-LAT2 clamps n≤2; lam floor 0.4; dual gate vs B4.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lat2_ops import (
    MAX_N,
    MIN_LAM,
    clamp_gene_lat2,
    decide_hlat2,
    mutate_gene_lat2,
    random_gene_lat2,
)


def test_given_large_n_when_clamp_lat2_then_n_at_most_max():
    g = clamp_gene_lat2(
        {
            "temperature": 0.8,
            "top_p": 0.9,
            "n": 6,
            "k": 4,
            "block": 2,
            "horizon": 2,
            "use_mae": False,
        }
    )
    assert 1 <= g["n"] <= MAX_N


def test_given_random_mutate_when_lat2_then_n_bounded():
    rng = random.Random(0)
    g = random_gene_lat2(rng)
    assert 1 <= g["n"] <= MAX_N
    for _ in range(20):
        g = mutate_gene_lat2(g, rng)
        assert 1 <= g["n"] <= MAX_N


def test_given_min_lam_when_defined_then_at_least_point_four():
    assert MIN_LAM >= 0.4


def test_given_faster_quality_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 100.0}}
    s = {"mean_lp": -16.9, "mean_wall": 70.0}
    assert decide_hlat2(s, stats).startswith("PROMOTE")


def test_given_no_wall_win_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.5, "mean_wall": 80.0}
    assert "no speedup" in decide_hlat2(s, stats)
