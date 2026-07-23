"""
Contract tests for nano_lm scorers and selection rules.
Contract source: docs/NANO-LM-TRACK.md — BoN/MAE commit = argmax score.
"""

from __future__ import annotations

import math
import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from scorers import distinct_n, mean_logprob, pick_argmax


def test_given_logprobs_when_mean_logprob_then_length_normalized():
    assert mean_logprob([-1.0, -3.0]) == pytest.approx(-2.0)


def test_given_empty_logprobs_when_mean_logprob_then_neg_inf():
    assert math.isinf(mean_logprob([])) and mean_logprob([]) < 0


def test_given_scores_when_pick_argmax_then_highest_index():
    # BoN / MAE commit rule
    assert pick_argmax([-2.0, -0.5, -1.0]) == 1


def test_given_tied_scores_when_pick_argmax_then_lowest_index():
    assert pick_argmax([1.0, 1.0, 0.5]) == 0


def test_given_empty_scores_when_pick_argmax_then_error():
    with pytest.raises(ValueError):
        pick_argmax([])


def test_given_tokens_when_distinct_1_then_unique_fraction():
    assert distinct_n([1, 2, 1, 3], 1) == pytest.approx(0.75)


def test_given_short_seq_when_distinct_2_then_zero():
    assert distinct_n([1], 2) == 0.0
