"""Wealth-tax helpers for H-TAX: scale elite float weights by (1−τ)."""

from __future__ import annotations

from typing import Sequence

import torch


def wealth_tax_factor(tau: float) -> float:
    """
    GIVEN tax rate τ
    WHEN computing the scale factor
    THEN return (1 − τ) with τ in [0, 1).
    """
    if not 0.0 <= tau < 1.0:
        raise ValueError("wealth_tax_factor: tau must be in [0, 1)")
    return 1.0 - tau


def apply_wealth_tax(
    state: dict[str, torch.Tensor], tau: float
) -> dict[str, torch.Tensor]:
    """
    GIVEN a state_dict and tax rate τ
    WHEN taxing elite wealth
    THEN floating tensors are scaled by (1−τ); non-floats are cloned.
    """
    factor = wealth_tax_factor(tau)
    out: dict[str, torch.Tensor] = {}
    for k, v in state.items():
        if v.dtype.is_floating_point:
            out[k] = v * factor
        else:
            out[k] = v.clone()
    return out


def elite_indices(fits: Sequence[float], elite_k: int) -> list[int]:
    """
    GIVEN fitness scores and elite_k
    WHEN choosing who to tax
    THEN return the elite_k highest-fitness indices (ties keep lower index).
    """
    if elite_k < 1:
        raise ValueError("elite_indices: elite_k must be >= 1")
    if elite_k > len(fits):
        raise ValueError("elite_indices: elite_k cannot exceed population")
    ranked = sorted(range(len(fits)), key=lambda i: (-fits[i], i))
    return ranked[:elite_k]
