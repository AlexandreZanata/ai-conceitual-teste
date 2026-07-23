"""
Contract: fossil vault push/pop + resurrect schedule; H-FOS decision vs H-SEL.
GIVEN vault and generation index
WHEN should_resurrect / vault_push / vault_pop run
THEN resurrection fires on schedule and FIFO order is preserved.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from fos_ops import should_resurrect, vault_pop, vault_push, worst_index
from matrix_report_lib import decision


def test_given_gen_when_every2_then_schedule():
    assert should_resurrect(0, 2) is False
    assert should_resurrect(1, 2) is True
    assert should_resurrect(2, 2) is False


def test_given_vault_when_push_over_max_then_drop_oldest():
    vault: list = []
    vault_push(vault, {"a": 1}, -1.0, max_size=2)
    vault_push(vault, {"a": 2}, -2.0, max_size=2)
    vault_push(vault, {"a": 3}, -3.0, max_size=2)
    assert len(vault) == 2
    assert vault[0]["state"]["a"] == 2


def test_given_vault_when_pop_then_fifo():
    vault: list = []
    vault_push(vault, {"a": 1}, 0.0, max_size=4)
    vault_push(vault, {"a": 2}, 0.0, max_size=4)
    first = vault_pop(vault)
    assert first["state"]["a"] == 1
    assert len(vault) == 1


def test_given_empty_when_pop_then_raises():
    with pytest.raises(ValueError):
        vault_pop([])


def test_given_fits_when_worst_then_lowest():
    assert worst_index([-1.0, -10.0, -2.0]) == 1


def test_given_better_than_hsel_when_hfos_then_promote():
    stats = {"H-SEL": {"mean_lp": -17.1}}
    assert decision("H-FOS", {"mean_lp": -16.9}, stats) == "PROMOTE (beats H-SEL)"


def test_given_worse_than_hsel_when_hfos_then_hold():
    stats = {"H-SEL": {"mean_lp": -17.0}}
    assert decision("H-FOS", {"mean_lp": -17.2}, stats) == "KILL / hold (≤ H-SEL)"
