"""Contract: Wave Z champion recipe schema + forbidden KILL stacks."""

from __future__ import annotations

from z_recipe import (
    FAMILY,
    FORBIDDEN,
    RECIPE_ID,
    ZERR_FAMILY,
    ZERR_RECIPE_ID,
    champion_recipe,
    validate_recipe,
)
from z_trial import validate_trial


def test_given_champion_when_validate_then_ok() -> None:
    r = champion_recipe(seed=0)
    assert validate_recipe(r) == []
    assert r["recipe_id"] == RECIPE_ID
    assert r["family"] == FAMILY
    assert r["pfb_k"] == 2
    assert r["qt_bits"] == 8


def test_given_zerr_recipe_when_validate_then_ok() -> None:
    r = champion_recipe(seed=0)
    r["recipe_id"] = ZERR_RECIPE_ID
    r["family"] = ZERR_FAMILY
    r["ckpt"] = "HZERR_seed0.pt"
    assert validate_recipe(r) == []


def test_given_k4_when_validate_then_err() -> None:
    r = champion_recipe()
    r["pfb_k"] = 4
    errs = validate_recipe(r)
    assert any("pfb_k" in e for e in errs)


def test_given_missing_forbidden_when_validate_then_err() -> None:
    r = champion_recipe()
    r["forbidden"] = ["STREAM"]
    errs = validate_recipe(r)
    assert any("GENCACHE" in e or "forbidden" in e for e in errs)
    for name in FORBIDDEN:
        assert name in FORBIDDEN


def test_given_trial_ok_when_validate_then_empty() -> None:
    t = {
        "trial_id": "Z1-01",
        "stage": "Z1",
        "question": "def add(a,b):?",
        "source_id": "prog:001",
        "recipe_id": RECIPE_ID,
        "completion": "return a+b",
        "score": 8.0,
        "error": False,
    }
    assert validate_trial(t) == []


def test_given_bad_score_when_validate_then_err() -> None:
    t = {
        "trial_id": "Z1-01",
        "stage": "Z1",
        "question": "x",
        "source_id": "prog:001",
        "recipe_id": RECIPE_ID,
        "completion": "y",
        "score": 11,
        "error": False,
    }
    assert any("score" in e for e in validate_trial(t))
