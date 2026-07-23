"""
Contract: CE top-k indices; teacher budget; H-LOFI vs H-FIT quality@wall.
GIVEN CE scores and k
WHEN top_k_indices runs
THEN the k highest scores are selected.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from lofi_ops import (
    decide_hlofi,
    teacher_forward_budget,
    top_k_indices,
    wall_saved,
)
from matrix_report_lib import decision


def test_given_scores_when_top_k_then_highest():
    assert top_k_indices([1.0, 5.0, 3.0, 4.0], 2) == [1, 3]


def test_given_bad_k_when_top_k_then_raises():
    with pytest.raises(ValueError):
        top_k_indices([1.0], 0)


def test_given_budget_when_k_lt_pop_then_wall_saved():
    lofi, full = teacher_forward_budget(
        pop_size=4, generations=3, n_prompts=2, top_k=2
    )
    assert lofi == 12 and full == 24
    assert wall_saved(lofi, full)
    assert not wall_saved(full, full)


def test_given_quality_and_save_when_hlofi_then_promote():
    stats = {"H-FIT": {"mean_lp": -16.8}}
    s = {"mean_lp": -16.7, "wall_save": 1.0}
    assert decide_hlofi(s, stats) == "PROMOTE (quality@wall vs H-FIT)"
    assert decision("H-LOFI", s, stats) == "PROMOTE (quality@wall vs H-FIT)"


def test_given_worse_quality_when_hlofi_then_kill():
    stats = {"H-FIT": {"mean_lp": -16.8}}
    s = {"mean_lp": -17.0, "wall_save": 1.0}
    assert decision("H-LOFI", s, stats) == "KILL (worse quality than H-FIT)"


def test_given_no_wall_save_when_hlofi_then_kill():
    stats = {"H-FIT": {"mean_lp": -16.8}}
    s = {"mean_lp": -16.7, "wall_save": 0.0}
    assert decision("H-LOFI", s, stats) == "KILL (no wall save)"
