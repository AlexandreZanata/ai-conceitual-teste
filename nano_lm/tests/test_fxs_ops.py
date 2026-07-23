"""
Contract: H-FXS breed = crossover→mutate→shock; decide vs max(H-FIT,H-XOV).
GIVEN two parents and a fresh init
WHEN breed_fxs_state runs
THEN shocked layer comes from fresh; other keys stay from crossover/mutate path.
"""

from __future__ import annotations

import random
import sys
from pathlib import Path

import pytest
import torch

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fxs_ops import PARENTS, breed_fxs_state, decide_hfxs
from matrix_report_lib import decision


def test_given_module_when_import_then_parents_named():
    assert PARENTS == ("H-FIT", "H-XOV", "H-SHO")


def test_given_parents_when_breed_then_shock_prefix_applied():
    rng = random.Random(0)
    a = {"h.0.w": torch.ones(2), "h.1.w": torch.ones(2) * 2}
    b = {"h.0.w": torch.ones(2) * 3, "h.1.w": torch.ones(2) * 4}
    fresh = {"h.0.w": torch.zeros(2), "h.1.w": torch.zeros(2) - 1}
    out, prefix = breed_fxs_state(a, b, fresh, ["h.0", "h.1"], rng, 0.0)
    assert prefix in {"h.0", "h.1"}
    shocked = [k for k in out if k == prefix or k.startswith(prefix + ".")]
    assert shocked
    for k in shocked:
        assert torch.equal(out[k], fresh[k])


def test_given_neg_scale_when_breed_then_raises():
    rng = random.Random(0)
    st = {"a": torch.ones(1)}
    with pytest.raises(ValueError):
        breed_fxs_state(st, st, st, ["a"], rng, -0.1)


def test_given_better_than_max_when_hfxs_then_promote():
    stats = {"H-FIT": {"mean_lp": -16.8}, "H-XOV": {"mean_lp": -16.3}}
    s = {"mean_lp": -16.0}
    assert decide_hfxs(s, stats) == "PROMOTE (beats max FIT/XOV)"
    assert decision("H-FXS", s, stats) == "PROMOTE (beats max FIT/XOV)"


def test_given_worse_than_max_when_hfxs_then_hold():
    stats = {"H-FIT": {"mean_lp": -16.8}, "H-XOV": {"mean_lp": -16.3}}
    s = {"mean_lp": -16.5}
    assert decision("H-FXS", s, stats) == "KILL / hold (≤ max FIT/XOV)"


def test_given_missing_control_when_hfxs_then_needs():
    assert decide_hfxs({"mean_lp": -16.0}, {"H-FIT": {"mean_lp": -17.0}}) == (
        "needs H-FIT+H-XOV control"
    )
