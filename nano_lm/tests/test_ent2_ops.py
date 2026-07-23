"""
Contract: TV floor penalty; H-ENT2 kill on collapse or ≤ B2.
GIVEN dual-head logits with TV below tau
WHEN tv_floor_loss runs
THEN penalty is positive; identical heads at tau yield ~tau.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ent2_ops import TV_TAU, decide_hent2, tv_floor_loss
from matrix_report_lib import decision


def test_given_identical_when_floor_then_positive():
    x = torch.randn(2, 4, 8)
    pen = float(tv_floor_loss(x, x, tau=TV_TAU).item())
    assert pen == pytest.approx(TV_TAU, rel=1e-4)


def test_given_far_heads_when_floor_then_zero():
    a = torch.zeros(1, 3, 4)
    b = torch.zeros(1, 3, 4)
    a[..., 0] = 10.0
    b[..., 1] = 10.0
    assert float(tv_floor_loss(a, b, tau=0.02).item()) == pytest.approx(0.0)


def test_given_bad_tau_when_floor_then_raises():
    x = torch.randn(1, 2, 3)
    with pytest.raises(ValueError):
        tv_floor_loss(x, x, tau=0.0)


def test_given_collapsed_when_hent2_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "collapsed": 1.0}
    assert decide_hent2(s, stats) == "KILL (collapsed again)"
    assert decision("H-ENT2", s, stats) == "KILL (collapsed again)"


def test_given_better_b2_distinct_when_hent2_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.5, "collapsed": 0.0}
    assert decision("H-ENT2", s, stats) == "PROMOTE (beats B2, heads distinct)"


def test_given_worse_b2_when_hent2_then_hold():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "collapsed": 0.0}
    assert decision("H-ENT2", s, stats) == "KILL / hold (≤ B2)"
