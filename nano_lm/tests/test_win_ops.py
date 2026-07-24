"""
Contract: H-WIN local window student; dual gate vs H-STAG.
"""

from __future__ import annotations

from student_model import build_student, count_params
from win_ops import decide_hwin, scale_flops_for_window
from win_student import build_win_student


def test_given_win_when_build_then_local_and_under_cap():
    m = build_win_student(window=32)
    assert count_params(m) <= 5_000_000
    assert m.config.attention_layers == ["local", "local"]
    assert int(m.config.window_size) == 32


def test_given_short_window_when_scale_then_attn_portion_shrinks():
    full = 100.0
    # seq=64, window=32 → ratio 0.5 → 0.75*100 + 0.25*50 wait: (1-0.25)+0.25*0.5 = 0.875
    assert scale_flops_for_window(full, seq_len=64, window=32) == 87.5
    assert scale_flops_for_window(full, seq_len=32, window=32) == 100.0


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_gflops": 12.0}
    stats = {"H-STAG": tip}
    assert decide_hwin({"mean_lp": -16.0, "mean_gflops": 10.0}, stats).startswith(
        "PROMOTE"
    )
    assert "quality" in decide_hwin({"mean_lp": -16.2, "mean_gflops": 8.0}, stats)
    assert "FLOP" in decide_hwin({"mean_lp": -15.9, "mean_gflops": 12.5}, stats)


def test_given_global_and_win_when_count_then_same_params():
    assert count_params(build_student()) == count_params(build_win_student())
