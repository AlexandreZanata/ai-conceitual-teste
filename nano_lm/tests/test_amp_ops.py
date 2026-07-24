"""
Contract: H-AMP resolves CUDA dtype; dual gate vs H-EARLY.
"""

from __future__ import annotations

import torch

from amp_ops import cast_student_amp, decide_hamp, resolve_amp_dtype
from student_model import build_student


def test_given_cpu_when_resolve_bf16_then_fp32():
    assert resolve_amp_dtype("bf16", torch.device("cpu")) == torch.float32


def test_given_cuda_when_resolve_fp16_then_half():
    if not torch.cuda.is_available():
        return
    assert resolve_amp_dtype("fp16", torch.device("cuda")) == torch.float16


def test_given_student_when_cast_then_dtype_matches():
    m = build_student()
    cast_student_amp(m, torch.float32)
    p = next(m.parameters())
    assert p.dtype == torch.float32


def test_given_dual_gate_when_decide_then_promote_or_kill():
    tip = {"mean_lp": -16.0, "mean_wall": 80.0}
    stats = {"H-EARLY": tip}
    assert decide_hamp({"mean_lp": -16.0, "mean_wall": 70.0}, stats).startswith(
        "PROMOTE"
    )
    assert "quality" in decide_hamp({"mean_lp": -16.2, "mean_wall": 50.0}, stats)
    assert "wall" in decide_hamp({"mean_lp": -15.9, "mean_wall": 90.0}, stats)
