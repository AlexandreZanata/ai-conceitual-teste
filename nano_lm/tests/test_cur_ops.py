"""
Contract: H-CUR length curriculum + decide vs B2.
"""

from __future__ import annotations

from cur_ops import DEFAULT_SEQ_LO, N_STAGES, cur_seq_len, decide_hcur


def test_given_stages_when_cur_seq_then_ends_and_few_values():
    assert cur_seq_len(0, 30, seq_lo=16, seq_hi=64) == 16
    assert cur_seq_len(29, 30, seq_lo=16, seq_hi=64) == 64
    vals = {cur_seq_len(i, 30, seq_lo=16, seq_hi=64) for i in range(30)}
    assert vals == {16, 40, 64}
    assert N_STAGES == 3


def test_given_bad_bounds_when_cur_seq_then_raises():
    try:
        cur_seq_len(0, 2, seq_lo=64, seq_hi=16)
        assert False, "expected ValueError"
    except ValueError:
        pass


def test_given_beats_b2_when_decide_then_promote():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hcur({"mean_lp": -16.5}, stats).startswith("PROMOTE")


def test_given_le_b2_when_decide_then_kill():
    stats = {"B2": {"mean_lp": -17.0}}
    assert decide_hcur({"mean_lp": -17.0}, stats) == "KILL (≤ B2)"
    assert DEFAULT_SEQ_LO == 16
