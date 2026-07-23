"""
Contract: fitness sharing subtracts α·mean L2; H-NIC needs diversity↑ and > H-SEL.
GIVEN raw fitness and weight vectors
WHEN share_fitness runs
THEN crowded individuals are penalized relative to isolated ones.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from nic_ops import mean_l2_to_others, share_fitness


def test_given_two_vecs_when_mean_l2_then_distance():
    a = torch.zeros(3)
    b = torch.tensor([3.0, 4.0, 0.0])
    assert mean_l2_to_others([a, b], 0) == pytest.approx(5.0)
    assert mean_l2_to_others([a, b], 1) == pytest.approx(5.0)


def test_given_crowd_when_share_then_penalizes_close_pair():
    # Individual 0 and 1 identical; 2 far away. Same raw fit.
    close = {"w": torch.zeros(2)}
    far = {"w": torch.tensor([10.0, 0.0])}
    raw = [1.0, 1.0, 1.0]
    shared = share_fitness(raw, [close, close, far], alpha=0.1)
    assert shared[2] > shared[0]
    assert shared[0] == pytest.approx(shared[1])


def test_given_alpha_zero_when_share_then_equals_raw():
    st = {"w": torch.ones(2)}
    shared = share_fitness([2.0, 3.0], [st, st], alpha=0.0)
    assert shared == pytest.approx([2.0, 3.0])


def test_given_no_div_up_when_hnic_then_kill():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "div_up_rate": 0.0}
    assert decision("H-NIC", s, stats) == "KILL (no diversity↑)"


def test_given_div_up_and_better_when_hnic_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "div_up_rate": 1.0}
    assert decision("H-NIC", s, stats) == "PROMOTE (beats H-SEL, diversity↑)"


def test_given_div_up_but_worse_when_hnic_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "div_up_rate": 1.0}
    assert decision("H-NIC", s, stats) == "KILL / hold (≤ H-SEL)"
