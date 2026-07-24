"""
Contract: H-CURL2 promotes only when some seq_lo beats tip lo=8.
"""

from __future__ import annotations

from curl2_ops import CURL2_CONTROL, CURL2_LOS, best_seq_lo, decide_hcurl2


def test_given_grid_when_constants_then_includes_tip():
    assert CURL2_CONTROL == 8
    assert CURL2_CONTROL in CURL2_LOS
    assert CURL2_LOS == (4, 6, 8, 10, 12)


def test_given_lo6_better_when_decide_then_promote():
    lp = {4: -17.0, 6: -16.0, 8: -16.5, 10: -16.8, 12: -16.7}
    assert decide_hcurl2(lp).startswith("PROMOTE")
    assert best_seq_lo(lp) == 6


def test_given_lo8_best_when_decide_then_kill():
    lp = {4: -17.0, 6: -16.8, 8: -16.0, 10: -16.5, 12: -16.2}
    assert "best seq_lo ≤ H-CURL" in decide_hcurl2(lp)


def test_given_missing_tip_when_decide_then_needs_control():
    assert "needs seq_lo=8" in decide_hcurl2({4: -16.0, 6: -15.0})
