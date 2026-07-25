"""Contract: int8 weight-only Linear replace reduces storage bytes."""

from __future__ import annotations

import torch
import torch.nn as nn

from qt_quant import (
    Int8WeightLinear,
    quantize_student_int8,
    weight_nbytes,
)


def test_given_linear_when_int8_forward_then_shape_ok() -> None:
    lin = nn.Linear(8, 4, bias=True)
    q = Int8WeightLinear(lin)
    x = torch.randn(2, 8)
    y = q(x)
    assert y.shape == (2, 4)
    assert q.weight_q.dtype == torch.int8


def test_given_module_when_quantize_then_bytes_drop() -> None:
    class Tiny(nn.Module):
        def __init__(self) -> None:
            super().__init__()
            self.a = nn.Linear(64, 64)
            self.b = nn.Linear(64, 32)

    fp = Tiny()
    before = weight_nbytes(fp)
    qt = quantize_student_int8(fp)
    after = weight_nbytes(qt)
    assert after < before
    assert any(isinstance(m, Int8WeightLinear) for m in qt.modules())
