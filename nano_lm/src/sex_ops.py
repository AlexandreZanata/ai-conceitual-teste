"""Mate-choice helpers for H-SEX: high fitness × high pairwise L2."""

from __future__ import annotations

from typing import Sequence

import torch


def state_l2(a: dict[str, torch.Tensor], b: dict[str, torch.Tensor]) -> float:
    """
    GIVEN two state_dicts with matching keys
    WHEN measuring genotype distance
    THEN return L2 over concatenated floating tensors (CPU).
    """
    if a.keys() != b.keys():
        raise ValueError("state_l2: key mismatch")
    parts_a: list[torch.Tensor] = []
    parts_b: list[torch.Tensor] = []
    for k, va in a.items():
        if not va.dtype.is_floating_point:
            continue
        parts_a.append(va.detach().float().reshape(-1).cpu())
        parts_b.append(b[k].detach().float().reshape(-1).cpu())
    if not parts_a:
        return 0.0
    return float(torch.norm(torch.cat(parts_a) - torch.cat(parts_b)).item())


def pairwise_l2(states: Sequence[dict[str, torch.Tensor]]) -> list[list[float]]:
    """Symmetric L2 matrix; diagonal is 0."""
    n = len(states)
    mat = [[0.0] * n for _ in range(n)]
    for i in range(n):
        for j in range(i + 1, n):
            d = state_l2(states[i], states[j])
            mat[i][j] = mat[j][i] = d
    return mat


def mate_affinity(fit_i: float, fit_j: float, dist: float, *, floor: float) -> float:
    """
    GIVEN two fitnesses, L2 distance, and a floor below all candidate fits
    WHEN scoring a mating pair
    THEN return (fit_i-floor)*(fit_j-floor)*dist (non-negative factors).
    """
    return (fit_i - floor) * (fit_j - floor) * dist


def choose_mate(
    i: int,
    candidates: Sequence[int],
    fits: Sequence[float],
    dist_row: Sequence[float],
) -> int:
    """
    GIVEN focal parent i and candidate indices
    WHEN choosing a mate
    THEN return argmax of mate_affinity among candidates ≠ i;
    if alone, return i (self-mate).
    """
    others = [j for j in candidates if j != i]
    if not others:
        return i
    floor = min(fits[j] for j in candidates) - 1e-6
    best_j = others[0]
    best_s = float("-inf")
    for j in others:
        s = mate_affinity(fits[i], fits[j], dist_row[j], floor=floor)
        if s > best_s:
            best_s = s
            best_j = j
    return best_j
