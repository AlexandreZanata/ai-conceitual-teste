"""
Contract: early-exit gate; gene codebooks; dual gate vs B4.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from early_ops import (
    MIN_NEWS,
    PATIENCES,
    clamp_early_gene,
    decide_hearly,
    mutate_early_gene,
    random_early_gene,
    should_early_exit,
)


def test_given_short_when_early_check_then_false():
    assert not should_early_exit(n_new=2, min_new=4, streak=3, patience=1)


def test_given_ready_when_early_check_then_true():
    assert should_early_exit(n_new=8, min_new=4, streak=2, patience=2)


def test_given_raw_when_clamp_then_on_codebooks():
    g = clamp_early_gene(
        {
            "min_new": 99,
            "patience": 9,
            "conf_threshold": 1.5,
            "n": 5,
            "temperature": 0.8,
            "top_p": 0.9,
        }
    )
    assert g["min_new"] in MIN_NEWS
    assert g["patience"] in PATIENCES
    assert 0.5 <= g["conf_threshold"] <= 0.99
    assert g["n"] in (1, 2)


def test_given_mutate_when_many_steps_then_stays_valid():
    rng = random.Random(0)
    g = random_early_gene(rng)
    for _ in range(20):
        g = mutate_early_gene(g, rng)
        assert g["min_new"] in MIN_NEWS
        assert g["patience"] in PATIENCES


def test_given_faster_quality_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 100.0}}
    s = {"mean_lp": -16.9, "mean_wall": 70.0}
    assert decide_hearly(s, stats).startswith("PROMOTE")


def test_given_no_speedup_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.5, "mean_wall": 80.0}
    assert "no speedup" in decide_hearly(s, stats)
