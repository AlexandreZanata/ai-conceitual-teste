"""Contract: Wave Z error bank schema + HITL stage pass bar (§9.5)."""

from __future__ import annotations

from pathlib import Path

from z_error_bank import (
    PASS_MAX_ERRORS,
    PASS_MEAN,
    append_error_row,
    stage_pass,
    validate_error_row,
)
from z_recipe import RECIPE_ID


def _row(**kwargs: object) -> dict[str, object]:
    base: dict[str, object] = {
        "trial_id": "Z1-01",
        "question": "def add(a,b):?",
        "source_id": "python-tutorial-intro",
        "model_raw": "........",
        "score": 1.0,
        "error": True,
        "recipe_id": RECIPE_ID,
        "gold": "def add(a, b):\n    return a + b\n",
    }
    base.update(kwargs)
    return base


def test_given_error_row_ok_when_validate_then_empty() -> None:
    assert validate_error_row(_row()) == []


def test_given_missing_model_raw_when_validate_then_err() -> None:
    row = _row()
    del row["model_raw"]
    assert any("model_raw" in e for e in validate_error_row(row))


def test_given_append_when_write_then_jsonl_grows(tmp_path: Path) -> None:
    path = tmp_path / "error_bank.jsonl"
    append_error_row(path, _row())
    append_error_row(path, _row(trial_id="Z1-02", score=2.0))
    lines = [ln for ln in path.read_text(encoding="utf-8").splitlines() if ln]
    assert len(lines) == 2


def test_given_ten_low_scores_when_stage_pass_then_fail() -> None:
    scores = [1.0] * 10
    gate = stage_pass(scores=scores, n_errors=10)
    assert gate["ok"] is False
    assert gate["mean"] == 1.0
    assert gate["pass_mean"] == PASS_MEAN
    assert gate["pass_max_errors"] == PASS_MAX_ERRORS


def test_given_pass_bar_when_stage_pass_then_ok() -> None:
    scores = [7.0, 8.0, 9.0, 7.0, 8.0, 7.5, 8.0, 9.0, 7.0, 8.0]
    gate = stage_pass(scores=scores, n_errors=2)
    assert gate["ok"] is True
    assert gate["mean"] >= PASS_MEAN
