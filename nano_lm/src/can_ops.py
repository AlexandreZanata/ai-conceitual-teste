"""Cannibalism helpers for H-CAN: winner copies loser LayerNorm tensors."""

from __future__ import annotations

from typing import Sequence

import torch


def is_layernorm_key(key: str) -> bool:
    """True for GPT-Neo-style ln_* weight/bias keys."""
    return ".ln_" in key or key.startswith("ln_")


def copy_layernorm(
    winner: dict[str, torch.Tensor],
    loser: dict[str, torch.Tensor],
) -> dict[str, torch.Tensor]:
    """
    GIVEN winner and loser state_dicts with matching keys
    WHEN cannibalizing
    THEN return a clone of winner where LayerNorm tensors come from loser.
    """
    if winner.keys() != loser.keys():
        raise ValueError("copy_layernorm: key mismatch")
    out: dict[str, torch.Tensor] = {}
    for k, wv in winner.items():
        if is_layernorm_key(k):
            out[k] = loser[k].clone()
        else:
            out[k] = wv.clone()
    return out


def pick_winner_loser(fits: Sequence[float]) -> tuple[int, int]:
    """
    GIVEN fitness scores
    WHEN choosing cannibal pair
    THEN return (winner, loser) = (argmax, argmin); if tied all-equal,
    loser is the next index modulo n.
    """
    n = len(fits)
    if n < 2:
        raise ValueError("pick_winner_loser: need pop_size >= 2")
    winner = max(range(n), key=lambda i: (fits[i], -i))
    loser = min(range(n), key=lambda i: (fits[i], i))
    if winner == loser:
        loser = (winner + 1) % n
    return winner, loser


def state_has_nan(state: dict[str, torch.Tensor]) -> bool:
    """True if any floating tensor contains NaN."""
    for v in state.values():
        if v.dtype.is_floating_point and bool(torch.isnan(v).any().item()):
            return True
    return False
