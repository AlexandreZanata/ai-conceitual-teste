"""
Contract: speculative verify accepts while u <= min(1, p/q); residual ≥ 0.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[1] / "src"
if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from spec_accept import accept_prefix_len, residual_probs


def test_given_ratio_ok_when_verify_then_accept_full_prefix():
    # GIVEN p/q >= 1 for all drafts and u < 1 WHEN verify THEN accept all
    n = accept_prefix_len([0.2, 0.3], [0.5, 0.4], [0.9, 0.9])
    assert n == 2


def test_given_low_ratio_when_verify_then_stop_at_first_reject():
    # GIVEN second token p/q = 0.1/0.4 = 0.25 and u=0.5 WHEN verify THEN n_ok=1
    n = accept_prefix_len([0.5, 0.4, 0.3], [0.6, 0.1, 0.5], [0.5, 0.5, 0.1])
    assert n == 1


def test_given_zero_draft_prob_when_verify_then_reject_immediately():
    n = accept_prefix_len([0.0, 0.4], [0.5, 0.4], [0.1, 0.1])
    assert n == 0


def test_given_p_minus_q_when_residual_then_nonneg_unit_mass():
    r = residual_probs([0.5, 0.3, 0.2], [0.4, 0.5, 0.1])
    assert all(x >= 0.0 for x in r)
    assert sum(r) == pytest.approx(1.0)
    assert r[1] == pytest.approx(0.0)  # p < q → mass 0
