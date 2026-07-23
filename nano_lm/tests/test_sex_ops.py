"""
Contract: mate affinity prefers high fit × high L2; H-SEX decision vs H-SEL.
GIVEN fitnesses and pairwise distances
WHEN choose_mate / mate_affinity run
THEN selected mate maximizes shifted fit product × distance.
"""

from __future__ import annotations

import sys
from pathlib import Path

import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from sex_ops import choose_mate, mate_affinity, pairwise_l2, state_l2


def test_given_known_vecs_when_state_l2_then_euclidean():
    a = {"w": torch.tensor([0.0, 0.0])}
    b = {"w": torch.tensor([3.0, 4.0])}
    assert state_l2(a, b) == 5.0


def test_given_three_states_when_pairwise_then_symmetric():
    s0 = {"w": torch.zeros(2)}
    s1 = {"w": torch.tensor([3.0, 4.0])}
    s2 = {"w": torch.tensor([0.0, 0.0])}
    m = pairwise_l2([s0, s1, s2])
    assert m[0][1] == 5.0 and m[1][0] == 5.0
    assert m[0][2] == 0.0
    assert m[0][0] == 0.0


def test_given_negative_fits_when_affinity_then_prefers_higher_fit():
    floor = -10.0 - 1e-6
    close_weak = mate_affinity(-10.0, -9.0, 10.0, floor=floor)
    far_strong = mate_affinity(-1.0, -1.0, 2.0, floor=floor)
    assert far_strong > close_weak


def test_given_candidates_when_choose_mate_then_farthest_fit_mate():
    # i=0 fit=-1; mates: j=1 fit=-2 dist=1; j=2 fit=-1.5 dist=10
    fits = [-1.0, -2.0, -1.5]
    dist_row = [0.0, 1.0, 10.0]
    assert choose_mate(0, [0, 1, 2], fits, dist_row) == 2


def test_given_alone_when_choose_mate_then_self():
    assert choose_mate(0, [0], [-1.0], [0.0]) == 0


def test_given_better_than_hsel_when_hsex_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-SEX", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hsex_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-SEX", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
