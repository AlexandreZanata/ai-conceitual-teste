"""
Contract: H-COMP compile helpers + decide vs H-EARLY.
"""

from __future__ import annotations

import torch

from comp_ops import COMPILE_MODE, compile_student, decide_hcomp, warmup_student
from student_model import build_student


def test_given_student_when_compile_then_callable():
    m = build_student().eval()
    device = torch.device("cpu")
    m = m.to(device)
    c = compile_student(m, mode="default")
    ids = torch.randint(0, 100, (1, 4), device=device)
    warmup_student(c, device, steps=1)
    with torch.no_grad():
        out = c(ids)
    assert out.logits.shape[0] == 1
    assert COMPILE_MODE == "reduce-overhead"


def test_given_wall_win_quality_when_decide_then_promote():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.45, "mean_wall": 40.0}
    assert decide_hcomp(s, stats).startswith("PROMOTE")


def test_given_quality_drop_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 50.0}}
    s = {"mean_lp": -16.7, "mean_wall": 30.0}
    assert "quality drop" in decide_hcomp(s, stats)


def test_given_no_wall_when_decide_then_kill():
    stats = {"H-EARLY": {"mean_lp": -16.5, "mean_wall": 40.0}}
    s = {"mean_lp": -16.4, "mean_wall": 45.0}
    assert "no wall win" in decide_hcomp(s, stats)
