"""
Contract: agreement/collapse metrics for H-ENT dual heads.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from ent_ops import agreement_loss, head_tv_distance, heads_collapsed
from matrix_report_lib import decision


def test_given_identical_logits_when_tv_then_near_zero():
    x = torch.randn(2, 4, 8)
    assert head_tv_distance(x, x) < 1e-5


def test_given_identical_when_agreement_then_near_zero():
    x = torch.randn(2, 4, 8)
    assert float(agreement_loss(x, x).item()) < 1e-5


def test_given_low_tv_when_collapse_check_then_true():
    assert heads_collapsed(0.01, floor=0.02) is True
    assert heads_collapsed(0.05, floor=0.02) is False


def test_given_collapsed_when_hent_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "collapsed": 1.0}
    assert decision("H-ENT", s, stats) == "KILL (collapsed to one head)"


def test_given_better_than_b2_when_hent_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.5, "collapsed": 0.0}
    assert decision("H-ENT", s, stats) == "PROMOTE (beats B2, heads distinct)"
