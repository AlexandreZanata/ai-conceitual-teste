"""Magnitude prune Linear weights; keep binary masks for recovery."""

from __future__ import annotations

from typing import Any

import torch
import torch.nn as nn

__all__ = [
    "linear_weight_params",
    "magnitude_prune",
    "apply_masks",
    "sparsity_of",
    "density_of",
]


def linear_weight_params(model: object) -> list[torch.nn.Parameter]:
    """Collect nn.Linear weight tensors (skip embeddings / biases)."""
    out: list[torch.nn.Parameter] = []
    for mod in model.modules():
        if isinstance(mod, nn.Linear):
            out.append(mod.weight)
    return out


def magnitude_prune(
    model: object, *, sparsity: float
) -> dict[str, torch.Tensor]:
    """
    GIVEN a student and target sparsity in (0,1)
    WHEN pruning
    THEN zero lowest-magnitude Linear weights; return name→mask.
    """
    s = float(sparsity)
    if not (0.0 < s < 1.0):
        raise ValueError("sparsity must be in (0,1)")
    weights = linear_weight_params(model)
    if not weights:
        return {}
    flat = torch.cat([w.detach().abs().reshape(-1) for w in weights])
    k = int(flat.numel() * s)
    if k < 1:
        return {}
    thresh = torch.topk(flat, k, largest=False).values.max()
    masks: dict[str, torch.Tensor] = {}
    for name, param in model.named_parameters():
        if param is None or param.ndim < 2:
            continue
        if not any(param is w for w in weights):
            continue
        mask = (param.detach().abs() > thresh).to(dtype=param.dtype)
        param.data.mul_(mask)
        masks[name] = mask
    return masks


def apply_masks(model: object, masks: dict[str, torch.Tensor]) -> None:
    """Re-apply binary masks after an optimizer step."""
    with torch.no_grad():
        for name, param in model.named_parameters():
            if name in masks:
                param.data.mul_(masks[name].to(device=param.device, dtype=param.dtype))


def sparsity_of(model: object) -> float:
    """Fraction of Linear weight elements that are exactly zero."""
    weights = linear_weight_params(model)
    if not weights:
        return 0.0
    zeros = sum(int((w == 0).sum().item()) for w in weights)
    total = sum(int(w.numel()) for w in weights)
    return float(zeros) / float(max(total, 1))


def density_of(model: object) -> float:
    return 1.0 - sparsity_of(model)
