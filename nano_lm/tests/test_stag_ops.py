"""
Contract: H-STAG promotes only when some n_stages beats tip stages=3.
"""

from __future__ import annotations

from stag_ops import STAG_CONTROL, STAG_SEQ_LO, STAG_STAGES, best_stages, decide_hstag


def test_given_grid_when_constants_then_includes_tip():
    assert STAG_CONTROL == 3
    assert STAG_SEQ_LO == 6
    assert STAG_CONTROL in STAG_STAGES
    assert STAG_STAGES == (2, 3, 4)


def test_given_st2_better_when_decide_then_promote():
    lp = {2: -13.0, 3: -13.3, 4: -13.4}
    assert decide_hstag(lp).startswith("PROMOTE")
    assert best_stages(lp) == 2


def test_given_st3_best_when_decide_then_kill():
    lp = {2: -13.5, 3: -13.0, 4: -13.2}
    assert "best n_stages ≤ H-CURL2" in decide_hstag(lp)


def test_given_missing_tip_when_decide_then_needs_control():
    assert "needs n_stages=3" in decide_hstag({2: -13.0, 4: -13.1})
