"""
Contract: linear ranks map worst→1 best→n; roulette prefers higher ranks.
GIVEN fitness vector
WHEN linear_rank_weights / select_parents_rank run
THEN weights match order and sampled parents stay in range.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from ran_ops import linear_rank_weights, linear_ranks, select_parents_rank


def test_given_fits_when_rank_weights_then_best_is_n():
    fits = [-10.0, -1.0, -5.0]
    assert linear_rank_weights(fits) == pytest.approx([1.0, 3.0, 2.0])
    assert linear_ranks(fits) == [1, 3, 2]


def test_given_ties_when_rank_then_lower_index_worse():
    fits = [1.0, 1.0]
    assert linear_ranks(fits) == [1, 2]


def test_given_count_when_select_rank_then_in_range():
    fits = [0.1, 0.2, 0.3, 0.0]
    parents = select_parents_rank(fits, 4, random.Random(1))
    assert len(parents) == 4
    assert all(0 <= i < 4 for i in parents)


def test_given_seq_rng_when_select_then_picks_expected():
    class SeqRng:
        def __init__(self, draws: list[float]) -> None:
            self._it = iter(draws)

        def random(self) -> float:
            return next(self._it)

    # weights [1,3,2] total=6; r*6 with r=0.0 → first bucket → idx 0
    assert select_parents_rank([-10.0, -1.0, -5.0], 1, SeqRng([0.0])) == [0]
    # r=0.5 → 3.0 into cumulative: 1 then 1+3=4 → idx 1
    assert select_parents_rank([-10.0, -1.0, -5.0], 1, SeqRng([0.5])) == [1]


def test_given_better_than_hsel_when_hran_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-RAN", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hran_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-RAN", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
