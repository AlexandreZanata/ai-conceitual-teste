"""
Contract: tournament_pick prefers higher fitness; H-TOU decision vs H-SEL.
GIVEN fitness vector and k draws
WHEN tournament_pick runs
THEN the winner is the max among sampled candidates.
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
from tou_ops import select_parents_tournament, tournament_pick


def test_given_candidates_when_tournament_then_argmax_among_draws():
    class SeqRng:
        def __init__(self, seq: list[int]) -> None:
            self._it = iter(seq)

        def randrange(self, n: int) -> int:
            v = next(self._it)
            assert 0 <= v < n
            return v

    # Draws indices 0, 2, 1 → fits -10, -5, -1 → winner index 1.
    assert tournament_pick([-10.0, -1.0, -5.0], 3, SeqRng([0, 2, 1])) == 1
    # Draws 2, 0, 2 → fits -5, -10, -5 → winner index 2.
    assert tournament_pick([-10.0, -1.0, -5.0], 3, SeqRng([2, 0, 2])) == 2


def test_given_k1_when_tournament_then_uniform_sample():
    fits = [0.0, 1.0, 2.0]
    rng = random.Random(7)
    picks = {tournament_pick(fits, 1, rng) for _ in range(80)}
    assert picks == {0, 1, 2}


def test_given_count_when_select_parents_then_length_matches():
    fits = [0.1, 0.2, 0.3, 0.0]
    parents = select_parents_tournament(fits, 4, 3, random.Random(1))
    assert len(parents) == 4
    assert all(0 <= i < 4 for i in parents)


def test_given_empty_when_tournament_then_raises():
    with pytest.raises(ValueError):
        tournament_pick([], 2, random.Random(0))


def test_given_better_than_hsel_when_htou_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-TOU", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_htou_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-TOU", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
