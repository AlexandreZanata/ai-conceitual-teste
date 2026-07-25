"""Int8 weight-only Linear replace for H-QT (mem↓; compute in activation dtype)."""

from __future__ import annotations

import copy

import torch
import torch.nn as nn
import torch.nn.functional as F

__all__ = [
    "Int8WeightLinear",
    "weight_nbytes",
    "quantize_student_int8",
]


class Int8WeightLinear(nn.Module):
    """Linear with int8 packed weights + per-out-channel scale."""

    def __init__(self, linear: nn.Linear) -> None:
        super().__init__()
        w = linear.weight.detach().float()
        scale = w.abs().amax(dim=1).clamp(min=1e-8) / 127.0
        q = torch.round(w / scale.unsqueeze(1)).clamp(-128, 127).to(torch.int8)
        self.register_buffer("weight_q", q.contiguous())
        self.register_buffer(
            "scale", scale.to(dtype=linear.weight.dtype).contiguous()
        )
        if linear.bias is None:
            self.bias = None
        else:
            self.bias = nn.Parameter(linear.bias.detach().clone())

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        w = self.weight_q.to(dtype=torch.float32) * self.scale.unsqueeze(1).float()
        w = w.to(dtype=x.dtype, device=x.device)
        bias = None if self.bias is None else self.bias.to(dtype=x.dtype)
        return F.linear(x, w, bias)


def weight_nbytes(model: nn.Module) -> int:
    """Sum storage bytes of parameters + buffers (weights/scales)."""
    total = 0
    for p in model.parameters():
        total += int(p.numel() * p.element_size())
    for b in model.buffers():
        total += int(b.numel() * b.element_size())
    return total


def quantize_student_int8(student: nn.Module) -> nn.Module:
    """
    GIVEN a student module with nn.Linear layers
    WHEN applying int8 weight-only replace
    THEN return a deep-copied model with Linear→Int8WeightLinear
         (skip lm_head to preserve embedding tie / avoid byte inflation).
    """
    model = copy.deepcopy(student)
    model.eval()
    replacements: list[tuple[nn.Module, str, Int8WeightLinear]] = []
    for _parent_name, parent in model.named_modules():
        for child_name, child in list(parent.named_children()):
            if child_name == "lm_head":
                continue
            if isinstance(child, nn.Linear):
                replacements.append(
                    (parent, child_name, Int8WeightLinear(child))
                )
    for parent, child_name, new_mod in replacements:
        setattr(parent, child_name, new_mod)
    model.eval()
    return model
