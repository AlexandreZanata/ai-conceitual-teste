"""Contract tests for student cap and quantum selection operators."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hyp_quantum import (
    amplitudes_from_scores,
    select_sup,
    select_uniform_bon,
)
from scorers import pick_argmax
from student_model import build_student, count_params


def test_given_student_when_built_then_params_at_most_5m():
    model = build_student()
    n = count_params(model)
    assert n <= 5_000_000
    assert n > 100_000


def test_given_scores_when_uniform_bon_then_matches_argmax():
    scores = [-2.0, -0.1, -1.0]
    assert select_uniform_bon(scores) == pick_argmax(scores) == 1


def test_given_amplitudes_when_normalized_then_unit_l2():
    amp = amplitudes_from_scores([0.0, 1.0, -1.0])
    norm = sum(a * a for a in amp) ** 0.5
    assert norm == pytest.approx(1.0, abs=1e-5)


def test_given_sup_when_select_then_valid_index():
    scores = [-1.0, -0.5, -2.0, -0.2]
    idx = select_sup(scores, seed=0)
    assert 0 <= idx < len(scores)
