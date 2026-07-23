"""Parasite-genome helpers for H-PAR: tiny vector steals selection credit."""

from __future__ import annotations

from typing import Sequence

import torch


def parasite_claim(parasite: torch.Tensor, steal_alpha: float) -> float:
    """
    GIVEN a parasite vector and steal_alpha ≥ 0
    WHEN computing stolen credit
    THEN return steal_alpha * tanh(mean(parasite)).
    """
    if steal_alpha < 0.0:
        raise ValueError("parasite_claim: steal_alpha must be >= 0")
    return steal_alpha * float(torch.tanh(parasite.float().mean()).item())


def selection_fitness(host_fit: float, claim: float) -> float:
    """Selection sees host fitness plus parasite claim (stolen credit)."""
    return host_fit + claim


def top_half_indices(fits: Sequence[float]) -> list[int]:
    """Indices of the best max(1, n//2) by fitness (ties keep lower index)."""
    n = len(fits)
    if n < 1:
        raise ValueError("top_half_indices: empty")
    k = max(1, n // 2)
    ranked = sorted(range(n), key=lambda i: (-fits[i], i))
    return ranked[:k]


def parents_diverge(host_fits: Sequence[float], sel_fits: Sequence[float]) -> bool:
    """
    GIVEN host and selection fitnesses
    WHEN comparing truncation parents
    THEN True iff the top-half index sets differ.
    """
    return set(top_half_indices(host_fits)) != set(top_half_indices(sel_fits))


def mutate_parasite(p: torch.Tensor, scale: float) -> torch.Tensor:
    """Clone parasite and add Gaussian noise of given scale."""
    return p + scale * torch.randn_like(p)
