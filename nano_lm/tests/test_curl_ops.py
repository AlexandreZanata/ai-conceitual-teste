"""
Contract: H-CURL promotes only when some seq_lo beats H-CUR (lo=16).
"""

from __future__ import annotations

from curl_ops import best_seq_lo, decide_hcurl, mean_lp_by_seq_lo


def test_given_rows_when_mean_by_lo_then_averages():
    rows = [
        {"seq_lo": 8, "teacher_mean_logprob": -10.0},
        {"seq_lo": 8, "teacher_mean_logprob": -12.0},
        {"seq_lo": 16, "teacher_mean_logprob": -11.0},
    ]
    assert mean_lp_by_seq_lo(rows) == {8: -11.0, 16: -11.0}


def test_given_lo8_better_when_decide_then_promote():
    lp = {8: -16.0, 16: -16.5, 32: -16.2}
    assert decide_hcurl(lp).startswith("PROMOTE")
    assert best_seq_lo(lp) == 8


def test_given_lo16_best_when_decide_then_kill():
    lp = {8: -17.0, 16: -16.0, 32: -16.5}
    assert "best seq_lo ≤ H-CUR" in decide_hcurl(lp)
