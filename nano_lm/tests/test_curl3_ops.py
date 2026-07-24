"""
Contract: H-CURL3 promotes only when some seq_lo beats tip lo=6.
"""

from __future__ import annotations

from curl3_ops import CURL3_CONTROL, CURL3_LOS, best_seq_lo, decide_hcurl3


def test_given_grid_when_constants_then_includes_tip():
    assert CURL3_CONTROL == 6
    assert CURL3_CONTROL in CURL3_LOS
    assert CURL3_LOS == (5, 6, 7)


def test_given_lo5_better_when_decide_then_promote():
    lp = {5: -13.0, 6: -13.3, 7: -13.4}
    assert decide_hcurl3(lp).startswith("PROMOTE")
    assert best_seq_lo(lp) == 5


def test_given_lo6_best_when_decide_then_kill():
    lp = {5: -13.5, 6: -13.0, 7: -13.2}
    assert "best seq_lo ≤ H-CURL2" in decide_hcurl3(lp)


def test_given_missing_tip_when_decide_then_needs_control():
    assert "needs seq_lo=6" in decide_hcurl3({5: -13.0, 7: -13.1})
