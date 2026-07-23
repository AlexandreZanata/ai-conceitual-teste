"""
Contract: elite-k selection and diversity collapse rules for H-ELI.
"""

from __future__ import annotations

import sys
from pathlib import Path

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from elite_ops import diversity_collapsed, fill_plan, select_elite_indices


def test_given_scores_when_elite_k2_then_top_two_indices():
    # GIVEN fits [-1, -3, -0.5, -2] WHEN elite_k=2 THEN indices 2 then 0
    assert select_elite_indices([-1.0, -3.0, -0.5, -2.0], 2) == [2, 0]


def test_given_tie_when_select_then_lower_index_wins():
    assert select_elite_indices([-1.0, -1.0, -2.0], 1) == [0]


def test_given_fill_plan_when_elite_k_then_prefix_elite():
    assert fill_plan(4, 2) == ["elite", "elite", "mutate", "mutate"]


def test_given_diversity_drop_when_check_then_collapsed():
    assert diversity_collapsed(10.0, 1.0, min_ratio=0.25) is True
    assert diversity_collapsed(10.0, 5.0, min_ratio=0.25) is False
    assert diversity_collapsed(10.0, 0.0) is True
