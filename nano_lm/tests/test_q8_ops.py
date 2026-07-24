"""
Contract: H-Q8 dynamic INT8 + decide vs H-CURL same-decode.
"""

from __future__ import annotations

import torch

from q8_ops import decide_hq8, has_dynamic_linear, quantize_student_dynamic
from student_model import build_student


def test_given_student_when_quantize_then_dynamic_linear():
    q = quantize_student_dynamic(build_student())
    assert has_dynamic_linear(q)
    ids = torch.randint(0, 100, (1, 8))
    with torch.no_grad():
        out = q(ids)
    assert out.logits.shape[-1] == q.config.vocab_size


def test_given_wall_win_quality_when_decide_then_promote():
    stats = {"H-CURL": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.45, "mean_wall": 40.0}
    assert decide_hq8(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-CURL": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.7, "mean_wall": 30.0}
    assert "quality drop" in decide_hq8(s, stats)


def test_given_no_wall_when_decide_then_kill():
    stats = {"H-CURL": {"mean_lp": -16.5, "mean_wall": 40.0}}
    s = {"mean_lp": -16.4, "mean_wall": 45.0}
    assert "no wall win" in decide_hq8(s, stats)
