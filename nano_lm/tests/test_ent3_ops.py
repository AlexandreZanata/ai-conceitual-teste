"""
Contract: soft TV / mix; H-ENT3 kill on collapse, chaos, or ≤ B2.
GIVEN dual-head logits
WHEN soft_tv and mix_logits run
THEN mix is average; identical heads have TV≈0.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ent3_ops import (
    collapse_or_chaos,
    decide_hent3,
    mix_logits,
    mode_chaos,
    soft_tv,
)
from matrix_report_lib import decision


def test_given_identical_when_soft_tv_then_near_zero():
    x = torch.randn(2, 4, 8)
    assert float(soft_tv(x, x).item()) < 1e-5


def test_given_heads_when_mix_then_average():
    a = torch.ones(1, 2, 3)
    b = torch.ones(1, 2, 3) * 3
    assert torch.allclose(mix_logits(a, b), torch.ones(1, 2, 3) * 2)


def test_given_high_tv_when_chaos_then_true():
    assert mode_chaos(0.95) is True
    assert mode_chaos(0.1) is False
    c, ch = collapse_or_chaos(0.005)
    assert c and not ch


def test_given_collapsed_when_hent3_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "collapsed": 1.0, "mode_chaos": 0.0}
    assert decide_hent3(s, stats) == "KILL (collapsed)"
    assert decision("H-ENT3", s, stats) == "KILL (collapsed)"


def test_given_chaos_when_hent3_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "collapsed": 0.0, "mode_chaos": 1.0}
    assert decision("H-ENT3", s, stats) == "KILL (mode chaos)"


def test_given_better_b2_when_hent3_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.5, "collapsed": 0.0, "mode_chaos": 0.0}
    assert decision("H-ENT3", s, stats) == "PROMOTE (beats B2, heads distinct)"
