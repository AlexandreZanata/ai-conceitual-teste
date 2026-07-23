"""
Contract: uniform blend picks tensors from a or b; H-XOV decision vs H-SEL.
GIVEN two state_dicts
WHEN blend_state_dicts runs with a controlled RNG
THEN floating keys follow the coin sequence; non-float always from a.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest
import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from xov_ops import blend_state_dicts, pick_parent_pair, pop_diversity


def test_given_coin_seq_when_blend_then_keys_from_a_or_b():
    class SeqRng:
        def __init__(self, coins: list[float]) -> None:
            self._it = iter(coins)

        def random(self) -> float:
            return next(self._it)

    a = {"w": torch.tensor([1.0]), "n": torch.tensor([7], dtype=torch.long)}
    b = {"w": torch.tensor([2.0]), "n": torch.tensor([9], dtype=torch.long)}
    out = blend_state_dicts(a, b, SeqRng([0.1, 0.9]))
    assert float(out["w"].item()) == pytest.approx(2.0)
    assert int(out["n"].item()) == 7
    out2 = blend_state_dicts(a, b, SeqRng([0.9]))
    assert float(out2["w"].item()) == pytest.approx(1.0)


def test_given_key_mismatch_when_blend_then_raises():
    a = {"w": torch.tensor([1.0])}
    b = {"x": torch.tensor([2.0])}
    with pytest.raises(ValueError):
        blend_state_dicts(a, b, random.Random(0))


def test_given_parents_when_pick_pair_then_in_range():
    i, j = pick_parent_pair(3, random.Random(1))
    assert 0 <= i < 3 and 0 <= j < 3


def test_given_identical_states_when_diversity_then_zero():
    st = {"w": torch.ones(4)}
    assert pop_diversity([st, dict(st)]) == pytest.approx(0.0)


def test_given_collapse_when_hxov_then_kill():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    s = {"mean_lp": -16.0, "collapsed": 1.0}
    assert decision("H-XOV", s, stats) == "KILL (diversity collapse)"


def test_given_better_than_hsel_when_hxov_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "collapsed": 0.0}
    assert decision("H-XOV", s, stats) == "PROMOTE (beats H-SEL, diversity ok)"
