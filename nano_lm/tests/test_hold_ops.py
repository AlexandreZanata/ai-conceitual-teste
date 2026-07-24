"""
Contract: holdout fit/eval ids disjoint; overfit gap; H-HOLD vs B2.
GIVEN fit and eval prompt id lists
WHEN assert_disjoint runs
THEN shared ids raise; empty overlap passes.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
ROOT = Path(__file__).resolve().parents[1]
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from hold_ops import (
    OVERFIT_GAP,
    assert_disjoint,
    attach_overfit,
    decide_hhold,
    is_overfit,
    load_prompt_ids,
    overfit_gap,
)


def test_given_fit_eval_files_when_ids_then_disjoint():
    fit = load_prompt_ids(ROOT / "prompts/fit_prompts.yaml")
    ev = load_prompt_ids(ROOT / "prompts/smoke_prompts.yaml")
    assert_disjoint(fit, ev)
    assert set(fit) & set(ev) == set()


def test_given_overlap_when_assert_then_raises():
    with pytest.raises(ValueError, match="overlap"):
        assert_disjoint(["p01", "f01"], ["p01", "p02"])


def test_given_gap_when_overfit_then_flag():
    assert overfit_gap(-15.0, -17.0) == pytest.approx(2.0)
    assert is_overfit(-15.0, -17.0, threshold=OVERFIT_GAP)
    assert not is_overfit(-16.5, -17.0, threshold=OVERFIT_GAP)


def test_given_row_when_attach_then_overfit_fields():
    row = attach_overfit({"teacher_mean_logprob": -18.0}, -15.0)
    assert row["overfit"] is True
    assert row["train_fit"] == -15.0
    assert row["overfit_gap"] == pytest.approx(3.0)


def test_given_overfit_when_hhold_then_kill():
    stats = {"B2": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.0, "overfit": 1.0}
    assert decide_hhold(s, stats) == "KILL (overfit train≫eval)"


def test_given_better_b2_no_overfit_when_hhold_then_promote():
    stats = {"B2": {"mean_lp": -17.1}}
    s = {"mean_lp": -16.9, "overfit": 0.0}
    assert decide_hhold(s, stats) == "PROMOTE (beats B2, holdout ok)"


def test_given_worse_b2_when_hhold_then_hold():
    stats = {"B2": {"mean_lp": -17.0}}
    s = {"mean_lp": -17.2, "overfit": 0.0}
    assert decide_hhold(s, stats) == "KILL / hold (≤ B2)"
