"""
Contract: draft genes stay on codebook; dual gate needs quality+speed vs B4.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from draft_ops import (
    DRAFT_LENS,
    clamp_draft_gene,
    decide_hdraft,
    mutate_draft_gene,
    random_draft_gene,
)


def test_given_raw_when_clamp_then_draft_len_in_codebook():
    g = clamp_draft_gene({"draft_len": 5, "temperature": 0.8, "top_p": 0.9})
    assert g["draft_len"] in DRAFT_LENS


def test_given_mutate_when_many_steps_then_stays_valid():
    rng = random.Random(0)
    g = random_draft_gene(rng)
    for _ in range(20):
        g = mutate_draft_gene(g, rng)
        assert g["draft_len"] in DRAFT_LENS
        assert 0.2 <= g["temperature"] <= 1.5
        assert 0.5 <= g["top_p"] <= 1.0


def test_given_faster_quality_when_decide_then_promote():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 100.0}}
    s = {"mean_lp": -16.9, "mean_wall": 70.0}
    assert decide_hdraft(s, stats).startswith("PROMOTE")


def test_given_no_speedup_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 50.0}}
    s = {"mean_lp": -16.5, "mean_wall": 80.0}
    assert "no speedup" in decide_hdraft(s, stats)


def test_given_quality_drop_when_decide_then_kill():
    stats = {"B4": {"mean_lp": -17.0, "mean_wall": 100.0}}
    s = {"mean_lp": -18.0, "mean_wall": 40.0}
    assert "quality drop" in decide_hdraft(s, stats)
