"""Contract: H-Q4 int4 pack + dual gate vs H-DEPTH."""

from __future__ import annotations

import torch
import torch.nn as nn

from q4_linear import Int4Linear, count_int4_linears, quantize_student_int4
from q4_ops import decide_hq4
from student_model import build_depth_student


def test_given_dual_gate_when_decide_then_promote_or_kill() -> None:
    tip = {"mean_lp": -12.0, "mean_wall": 100.0}
    stats = {"H-DEPTH": tip}
    assert decide_hq4(
        {"mean_lp": -12.0, "mean_wall": 80.0}, stats
    ).startswith("PROMOTE")
    assert "quality" in decide_hq4(
        {"mean_lp": -12.2, "mean_wall": 50.0}, stats
    )
    assert "wall" in decide_hq4(
        {"mean_lp": -11.9, "mean_wall": 100.0}, stats
    )


def test_given_linear_when_int4_then_close_to_fp() -> None:
    # GIVEN bf16 Linear / WHEN int4 replace / THEN output ≈ fp (atol loose)
    if not torch.cuda.is_available():
        return
    torch.manual_seed(0)
    lin = nn.Linear(64, 64, bias=False).cuda().to(torch.bfloat16)
    parent = nn.Sequential(lin)
    x = torch.randn(2, 8, 64, device="cuda", dtype=torch.bfloat16)
    with torch.no_grad():
        ref = lin(x).float()
        quantize_student_int4(parent)
        assert count_int4_linears(parent) == 1
        assert isinstance(parent[0], Int4Linear)
        out = parent(x).float()
    assert torch.allclose(out, ref, atol=0.35, rtol=0.05)


def test_given_depth_student_when_quantize_then_skips_lm_head() -> None:
    if not torch.cuda.is_available():
        return
    m = build_depth_student().cuda().eval()
    quantize_student_int4(m)
    assert count_int4_linears(m) >= 4
    assert isinstance(m.lm_head, nn.Linear)
