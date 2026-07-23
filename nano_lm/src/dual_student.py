"""Dual-head student: shared body + shared noise + two light projections."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

from student_model import build_student, count_params


class DualHeadStudent(nn.Module):
    """Shared transformer; two proj paths into shared lm_head; shared noise."""

    def __init__(self, base: Any, *, noise_std: float = 0.01) -> None:
        super().__init__()
        self.base = base
        hidden = int(base.config.hidden_size)
        self.proj_a = nn.Linear(hidden, hidden, bias=False)
        self.proj_b = nn.Linear(hidden, hidden, bias=False)
        self.noise_std = noise_std
        nn.init.eye_(self.proj_a.weight)
        nn.init.eye_(self.proj_b.weight)
        # tiny break symmetry
        with torch.no_grad():
            self.proj_b.weight.add_(0.01 * torch.randn_like(self.proj_b.weight))

    def forward_dual(
        self, input_ids: torch.Tensor
    ) -> tuple[torch.Tensor, torch.Tensor]:
        hidden = self.base.transformer(input_ids=input_ids).last_hidden_state
        if self.training and self.noise_std > 0:
            noise = torch.randn_like(hidden) * self.noise_std
        else:
            noise = 0.0
        ha = self.proj_a(hidden + noise)
        hb = self.proj_b(hidden + noise)
        return self.base.lm_head(ha), self.base.lm_head(hb)

    def forward(self, input_ids: torch.Tensor) -> Any:
        """Mean-head logits for decode/eval compatibility."""
        la, lb = self.forward_dual(input_ids)
        out = type("Out", (), {})()
        out.logits = 0.5 * (la + lb)
        return out


def build_dual_student(vocab_size: int = 50257, *, noise_std: float = 0.01) -> DualHeadStudent:
    base = build_student(vocab_size)
    dual = DualHeadStudent(base, noise_std=noise_std)
    n = count_params(dual)
    if n > 5_000_000:
        raise RuntimeError(f"dual student has {n} params (>5M cap)")
    return dual
