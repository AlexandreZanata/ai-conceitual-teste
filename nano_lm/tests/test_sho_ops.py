"""
Contract: layer shock reinit; H-SHO decision vs H-SEL (plain mutate).
GIVEN state keys and a fresh init
WHEN shock_state runs for a prefix
THEN only that layer is replaced from fresh.
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
from sho_ops import keys_for_prefix, layer_prefixes, pick_prefix, shock_state


def test_given_keys_when_prefixes_then_blocks():
    keys = [
        "transformer.wte.weight",
        "transformer.h.0.ln_1.weight",
        "transformer.h.1.mlp.c_fc.weight",
        "lm_head.weight",
    ]
    assert layer_prefixes(keys) == [
        "lm_head",
        "transformer.h.0",
        "transformer.h.1",
        "transformer.wte",
    ]


def test_given_prefix_when_shock_then_only_layer_replaced():
    state = {
        "transformer.h.0.w": torch.ones(2),
        "transformer.h.1.w": torch.ones(2) * 2,
        "lm_head.weight": torch.ones(2) * 3,
    }
    fresh = {
        "transformer.h.0.w": torch.zeros(2),
        "transformer.h.1.w": torch.zeros(2) - 1,
        "lm_head.weight": torch.zeros(2) - 2,
    }
    out = shock_state(state, fresh, "transformer.h.0")
    assert torch.equal(out["transformer.h.0.w"], fresh["transformer.h.0.w"])
    assert torch.equal(out["transformer.h.1.w"], state["transformer.h.1.w"])
    assert keys_for_prefix(list(state), "lm_head") == ["lm_head.weight"]


def test_given_index_when_pick_then_wraps():
    assert pick_prefix(["a", "b"], 3) == "b"
    with pytest.raises(ValueError):
        pick_prefix([], 0)


def test_given_better_than_hsel_when_hsho_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-SHO", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hsho_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-SHO", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
