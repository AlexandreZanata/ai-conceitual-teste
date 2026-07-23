"""
Contract: winner copies loser LayerNorm keys; H-CAN decision vs H-SEL / NaN.
GIVEN winner and loser state_dicts
WHEN copy_layernorm runs
THEN only ln_* tensors come from loser; other keys stay from winner.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest
import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from can_ops import (
    copy_layernorm,
    is_layernorm_key,
    pick_winner_loser,
    state_has_nan,
)
from matrix_report_lib import decision


def test_given_keys_when_is_ln_then_detect():
    assert is_layernorm_key("transformer.h.0.ln_1.weight")
    assert is_layernorm_key("transformer.ln_f.bias")
    assert not is_layernorm_key("transformer.h.0.attn.attention.k_proj.weight")


def test_given_states_when_copy_ln_then_only_ln_from_loser():
    w = {
        "transformer.h.0.ln_1.weight": torch.tensor([1.0]),
        "other.weight": torch.tensor([3.0]),
    }
    loser = {
        "transformer.h.0.ln_1.weight": torch.tensor([9.0]),
        "other.weight": torch.tensor([7.0]),
    }
    out = copy_layernorm(w, loser)
    assert float(out["transformer.h.0.ln_1.weight"]) == pytest.approx(9.0)
    assert float(out["other.weight"]) == pytest.approx(3.0)


def test_given_fits_when_pick_then_winner_loser():
    assert pick_winner_loser([-1.0, -10.0, -2.0]) == (0, 1)


def test_given_nan_when_check_then_true():
    st = {"w": torch.tensor([1.0, float("nan")])}
    assert state_has_nan(st) is True
    assert state_has_nan({"w": torch.ones(2)}) is False


def test_given_nan_when_hcan_then_kill():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "nan": 1.0}
    assert decision("H-CAN", s, stats) == "KILL (NaN)"


def test_given_better_than_hsel_when_hcan_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "nan": 0.0}
    assert decision("H-CAN", s, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hcan_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "nan": 0.0}
    assert decision("H-CAN", s, stats) == "KILL / hold (≤ H-SEL)"
