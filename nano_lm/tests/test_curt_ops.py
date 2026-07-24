"""
Contract: H-CURT decide vs H-CUR tip.
"""

from __future__ import annotations

from curt_ops import CURT_SEQ_LO, CURT_STAGES, decide_hcurt


def test_given_constants_when_import_then_formal_tip():
    assert CURT_STAGES == 5
    assert CURT_SEQ_LO == 8


def test_given_beats_tip_when_decide_then_promote():
    stats = {"H-CUR": {"mean_lp": -17.0}}
    assert decide_hcurt({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_tip_when_decide_then_kill():
    stats = {"H-CUR": {"mean_lp": -17.0}}
    assert decide_hcurt({"mean_lp": -17.0}, stats) == "KILL (≤ H-CUR tip)"
