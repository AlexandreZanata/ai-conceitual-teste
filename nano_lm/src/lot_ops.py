"""H-LOT: sparse lottery-ticket masks; decide vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn as nn

__all__ = [
    "CLIFF_LP",
    "magnitude_keep_mask",
    "collect_linear_inits",
    "build_magnitude_masks",
    "apply_weight_masks",
    "rewind_linears",
    "mask_keep_frac",
    "decide_hlot",
]

CLIFF_LP = 0.5


def magnitude_keep_mask(weight: torch.Tensor, keep_frac: float) -> torch.Tensor:
    """
    GIVEN a weight tensor and keep_frac in (0,1]
    WHEN building a lottery mask
    THEN keep the top-|w| fraction (at least one element).
    """
    if not (0.0 < float(keep_frac) <= 1.0):
        raise ValueError("magnitude_keep_mask: keep_frac must be in (0,1]")
    flat = weight.detach().abs().reshape(-1)
    k = max(1, int(round(float(keep_frac) * flat.numel())))
    if k >= flat.numel():
        return torch.ones_like(weight)
    thresh = torch.topk(flat, k, largest=True).values.min()
    return (weight.detach().abs() >= thresh).to(dtype=weight.dtype)


def collect_linear_inits(model: nn.Module) -> dict[str, torch.Tensor]:
    """Snapshot initial Linear.weight tensors by module name."""
    return {
        n: m.weight.detach().clone()
        for n, m in model.named_modules()
        if isinstance(m, nn.Linear)
    }


def build_magnitude_masks(
    model: nn.Module, keep_frac: float
) -> dict[str, torch.Tensor]:
    """Magnitude keep-masks for every Linear weight."""
    return {
        n: magnitude_keep_mask(m.weight, keep_frac)
        for n, m in model.named_modules()
        if isinstance(m, nn.Linear)
    }


def apply_weight_masks(model: nn.Module, masks: Mapping[str, torch.Tensor]) -> None:
    """Zero pruned weights in-place (no grad)."""
    with torch.no_grad():
        for n, m in model.named_modules():
            if n in masks and isinstance(m, nn.Linear):
                m.weight.mul_(masks[n].to(device=m.weight.device, dtype=m.weight.dtype))


def rewind_linears(
    model: nn.Module,
    inits: Mapping[str, torch.Tensor],
    masks: Mapping[str, torch.Tensor],
) -> None:
    """
    GIVEN init snapshots and masks
    WHEN rewinding the ticket
    THEN set weight ← init ⊙ mask.
    """
    with torch.no_grad():
        for n, m in model.named_modules():
            if n not in inits or n not in masks or not isinstance(m, nn.Linear):
                continue
            init = inits[n].to(device=m.weight.device, dtype=m.weight.dtype)
            mask = masks[n].to(device=m.weight.device, dtype=m.weight.dtype)
            m.weight.copy_(init * mask)


def mask_keep_frac(masks: Mapping[str, torch.Tensor]) -> float:
    """Fraction of weights kept across all masks."""
    kept = sum(float(m.sum().item()) for m in masks.values())
    total = sum(float(m.numel()) for m in masks.values())
    return kept / max(total, 1.0)


def decide_hlot(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-LOT vs B2
    WHEN deciding
    THEN PROMOTE if > B2; KILL quality cliff if Δ < −CLIFF; else KILL ≤ B2.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    delta = float(s["mean_lp"]) - float(b2["mean_lp"])
    if delta > 1e-6:
        return "PROMOTE (beats B2)"
    if delta < -CLIFF_LP:
        return "KILL (quality cliff)"
    return "KILL (≤ B2)"
