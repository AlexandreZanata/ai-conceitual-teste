"""
Contract: wealth tax scales elite float weights by (1−τ); H-TAX vs H-SEL.
GIVEN a state_dict and tax rate
WHEN apply_wealth_tax runs
THEN floating tensors shrink by (1−τ); non-floats unchanged.
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
from tax_ops import apply_wealth_tax, elite_indices, wealth_tax_factor


def test_given_tau_when_factor_then_one_minus_tau():
    assert wealth_tax_factor(0.05) == pytest.approx(0.95)


def test_given_bad_tau_when_factor_then_raises():
    with pytest.raises(ValueError):
        wealth_tax_factor(1.0)
    with pytest.raises(ValueError):
        wealth_tax_factor(-0.1)


def test_given_state_when_tax_then_floats_scaled():
    st = {
        "w": torch.tensor([2.0, 4.0]),
        "n": torch.tensor([7], dtype=torch.long),
    }
    out = apply_wealth_tax(st, 0.5)
    assert float(out["w"][0]) == pytest.approx(1.0)
    assert float(out["w"][1]) == pytest.approx(2.0)
    assert int(out["n"].item()) == 7


def test_given_fits_when_elite_then_top_k():
    fits = [-10.0, -1.0, -5.0, -2.0]
    assert elite_indices(fits, 2) == [1, 3]


def test_given_better_than_hsel_when_htax_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-TAX", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_htax_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-TAX", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
