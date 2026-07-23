"""
Contract: Goldilocks score peaks at mid; H-GLD decision vs max-lp H-FIT.
GIVEN raw teacher_lp and band (mid, width)
WHEN goldilocks_score runs
THEN closer-to-mid ranks higher; extremes are punished.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from gld_ops import goldilocks_score, goldilocks_scores
from matrix_report_lib import decision


def test_given_mid_when_score_then_zero_penalty():
    assert goldilocks_score(-17.0, mid=-17.0, width=2.0) == pytest.approx(0.0)


def test_given_extreme_when_score_then_worse_than_near():
    mid, w = -17.0, 2.0
    near = goldilocks_score(-17.5, mid=mid, width=w)
    far = goldilocks_score(-20.0, mid=mid, width=w)
    assert near > far


def test_given_bad_width_when_score_then_raises():
    with pytest.raises(ValueError):
        goldilocks_score(-17.0, mid=-17.0, width=0.0)


def test_given_raws_when_scores_then_aligned():
    out = goldilocks_scores([-17.0, -19.0], mid=-17.0, width=2.0)
    assert out[0] > out[1]


def test_given_better_than_hfit_when_hgld_then_promote():
    stats = {"H-FIT": {"mean_lp": -17.1}}
    assert decision("H-GLD", {"mean_lp": -16.9}, stats) == (
        "PROMOTE (beats max-lp / H-FIT)"
    )


def test_given_worse_than_hfit_when_hgld_then_hold():
    stats = {"H-FIT": {"mean_lp": -17.0}}
    assert decision("H-GLD", {"mean_lp": -17.2}, stats) == (
        "KILL / hold (≤ max-lp fitness)"
    )


def test_given_no_hfit_when_hgld_then_needs_control():
    assert decision("H-GLD", {"mean_lp": -16.0}, {}) == "needs H-FIT control"
