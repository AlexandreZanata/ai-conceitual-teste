"""
Contract: seasonal fitness alternates CE / teacher_lp; H-SEA vs H-FIT.
GIVEN 0-based generation index
WHEN season_kind runs
THEN even → teacher_lp; odd → ce.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from matrix_report_lib import decision
from sea_ops import is_ce_season, season_kind


def test_given_even_gen_when_season_then_teacher_lp():
    assert season_kind(0) == "teacher_lp"
    assert season_kind(2) == "teacher_lp"
    assert is_ce_season(0) is False


def test_given_odd_gen_when_season_then_ce():
    assert season_kind(1) == "ce"
    assert season_kind(3) == "ce"
    assert is_ce_season(1) is True


def test_given_negative_gen_when_season_then_raises():
    with pytest.raises(ValueError):
        season_kind(-1)


def test_given_better_than_hfit_when_hsea_then_promote():
    stats = {"H-FIT": {"mean_lp": -17.1}}
    assert decision("H-SEA", {"mean_lp": -16.9}, stats) == (
        "PROMOTE (beats max-lp / H-FIT)"
    )


def test_given_worse_than_hfit_when_hsea_then_hold():
    stats = {"H-FIT": {"mean_lp": -17.0}}
    assert decision("H-SEA", {"mean_lp": -17.2}, stats) == (
        "KILL / hold (≤ max-lp fitness)"
    )
