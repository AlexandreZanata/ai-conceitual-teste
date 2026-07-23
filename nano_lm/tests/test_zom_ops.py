"""
Contract: zombie = −weights + noise; H-ZOM decision vs H-SEL / diverge.
GIVEN a dead state_dict
WHEN zombie_state runs
THEN floating tensors are negated then noised; dead_indices are the worst half.
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
from zom_ops import dead_indices, state_diverged, zombie_state


def test_given_state_when_zombie_zero_noise_then_negated():
    torch.manual_seed(0)
    st = {"w": torch.tensor([2.0, -4.0]), "n": torch.tensor([1], dtype=torch.long)}
    # scale=0 → pure sign flip
    out = zombie_state(st, 0.0)
    assert float(out["w"][0]) == pytest.approx(-2.0)
    assert float(out["w"][1]) == pytest.approx(4.0)
    assert int(out["n"].item()) == 1


def test_given_fits_when_dead_then_worst_half():
    assert dead_indices([-1.0, -10.0, -2.0, -9.0]) == [1, 3]


def test_given_inf_when_diverged_then_true():
    assert state_diverged({"w": torch.tensor([float("inf")])}) is True
    assert state_diverged({"w": torch.ones(2)}) is False


def test_given_nan_when_hzom_then_kill():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "nan": 1.0}
    assert decision("H-ZOM", s, stats) == "KILL (NaN)"


def test_given_better_than_hsel_when_hzom_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "nan": 0.0}
    assert decision("H-ZOM", s, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hzom_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "nan": 0.0}
    assert decision("H-ZOM", s, stats) == "KILL / hold (≤ H-SEL)"
