"""
Contract: parasite claim shifts selection fitness; H-PAR decision vs H-SEL.
GIVEN host fitness and parasite vector
WHEN selection_fitness / parents_diverge run
THEN claim = α·tanh(mean(p)) and diverge detects parent-set mismatch.
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
from par_ops import (
    mutate_parasite,
    parents_diverge,
    parasite_claim,
    selection_fitness,
    top_half_indices,
)


def test_given_parasite_when_claim_then_alpha_tanh_mean():
    p = torch.zeros(4)
    assert parasite_claim(p, 0.5) == pytest.approx(0.0)
    p2 = torch.ones(4) * 10.0
    assert parasite_claim(p2, 0.5) == pytest.approx(0.5, abs=1e-3)


def test_given_claim_when_selection_then_host_plus_claim():
    assert selection_fitness(-10.0, 0.5) == pytest.approx(-9.5)


def test_given_fits_when_top_half_then_best():
    assert top_half_indices([-1.0, -10.0, -2.0, -9.0]) == [0, 2]


def test_given_mismatch_when_diverge_then_true():
    host = [-1.0, -2.0, -10.0, -11.0]
    sel = [-11.0, -10.0, -1.0, -2.0]
    assert parents_diverge(host, sel) is True
    assert parents_diverge(host, host) is False


def test_given_parasite_when_mutate_then_same_shape():
    p = torch.zeros(8)
    out = mutate_parasite(p, 0.1)
    assert out.shape == p.shape


def test_given_dominates_when_hpar_then_kill():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "parasite_dominates": 1.0}
    assert decision("H-PAR", s, stats) == "KILL (parasite dominates)"


def test_given_better_than_hsel_when_hpar_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "parasite_dominates": 0.0}
    assert decision("H-PAR", s, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hpar_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "parasite_dominates": 0.0}
    assert decision("H-PAR", s, stats) == "KILL / hold (≤ H-SEL)"
