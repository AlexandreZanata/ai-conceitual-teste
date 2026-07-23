"""
Contract: beam genes stay on codebook; dual gate needs quality+speed vs B4.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from beam_ops import (
    BEAM_WIDTHS,
    clamp_beam_gene,
    decide_hbeam,
    mutate_beam_gene,
    random_beam_gene,
)
from decode_beam import _beam_score


def test_given_raw_when_clamp_then_width_in_codebook():
    g = clamp_beam_gene({"beam_width": 6, "length_penalty": 3.0})
    assert g["beam_width"] in BEAM_WIDTHS
    assert 0.0 <= g["length_penalty"] <= 2.0


def test_given_mutate_when_many_steps_then_stays_valid():
    rng = random.Random(0)
    g = random_beam_gene(rng)
    for _ in range(20):
        g = mutate_beam_gene(g, rng)
        assert g["beam_width"] in BEAM_WIDTHS
        assert 0.0 <= g["length_penalty"] <= 2.0


def test_given_positive_penalty_when_longer_same_sum_then_less_negative():
    # Standard length-norm: same cumulative log_sum → longer scores higher.
    assert _beam_score(-10.0, 4, 1.0) > _beam_score(-10.0, 2, 1.0)


def test_given_zero_penalty_when_score_then_equals_log_sum():
    assert _beam_score(-7.5, 3, 0.0) == -7.5


def test_given_faster_quality_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 100.0}}
    s = {"mean_lp": -16.9, "mean_wall": 70.0}
    assert decide_hbeam(s, stats).startswith("PROMOTE")


def test_given_no_speedup_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.5, "mean_wall": 80.0}
    assert "no speedup" in decide_hbeam(s, stats)
