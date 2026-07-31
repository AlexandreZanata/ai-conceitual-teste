"""Contracts for P00 hardware profiling and budget derivation."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from bench.compute_budget import compute_budget
from bench.hw_profile import (
    FLOPS_PER_MATMUL,
    relative_delta,
    tflops_from_seconds,
    write_json,
)


def test_tflops_from_seconds_is_positive_for_valid_timing() -> None:
    # 137e9 FLOPs in 0.01 s → 13.7 TFLOP/s
    value = tflops_from_seconds(0.01)
    assert value == pytest.approx(FLOPS_PER_MATMUL / 0.01 / 1e12)
    assert value > 0


def test_tflops_from_seconds_rejects_non_positive_time() -> None:
    assert tflops_from_seconds(0.0) == 0.0
    assert tflops_from_seconds(-1.0) == 0.0


def test_relative_delta_within_ten_percent_gate() -> None:
    assert relative_delta(20.0, 21.5) < 0.10
    assert relative_delta(20.0, 25.0) > 0.10


def test_compute_budget_emits_feasible_flag() -> None:
    profile = {
        "git_hash": "abc",
        "seed": 0,
        "wall_seconds": 600.0,
        "sustained_bf16_tflops": {"tflops_final_minute_median": 20.0},
        "held_out_bpb": None,
        "embedding_params": None,
        "non_embedding_params": None,
    }
    budget = compute_budget(profile, params=42_200_000, tokens=4e9, mfu=0.25)
    assert "feasible" in budget
    assert isinstance(budget["feasible"], bool)
    assert budget["predicted_wall_hours"] > 0
    assert budget["max_tokens_in_72h"] > 0
    assert budget["max_params_at_4b_tokens_in_72h"] > 0


def test_compute_budget_marks_infeasible_when_too_slow() -> None:
    profile = {
        "git_hash": "abc",
        "seed": 0,
        "wall_seconds": 1.0,
        "sustained_bf16_tflops": {"tflops_final_minute_median": 0.1},
        "held_out_bpb": None,
        "embedding_params": None,
        "non_embedding_params": None,
    }
    budget = compute_budget(profile, params=42_200_000, tokens=4e9, mfu=0.25)
    assert budget["feasible"] is False


def test_compute_budget_rejects_zero_sustained() -> None:
    profile = {
        "sustained_bf16_tflops": {"tflops_final_minute_median": 0.0},
    }
    with pytest.raises(ValueError):
        compute_budget(profile, params=1.0, tokens=1.0, mfu=0.25)


def test_write_json_roundtrip(tmp_path: Path) -> None:
    path = tmp_path / "profile.json"
    payload = {"git_hash": "deadbeef", "seed": 0, "value": 1.5}
    write_json(path, payload)
    loaded = json.loads(path.read_text(encoding="utf-8"))
    assert loaded == payload
