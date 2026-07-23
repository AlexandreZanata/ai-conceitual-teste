"""Shared scoring and selection contracts for nano_lm decode methods."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Sequence


@dataclass(frozen=True)
class DecodeResult:
    token_ids: tuple[int, ...]
    text: str
    mean_logprob: float
    wall_ms: float
    token_evals: int


def mean_logprob(logprobs: Sequence[float]) -> float:
    """Length-normalized mean log-probability; empty -> -inf."""
    if not logprobs:
        return float("-inf")
    return sum(logprobs) / len(logprobs)


def pick_argmax(scores: Sequence[float]) -> int:
    """
    Contract: commit the highest score; ties keep the lowest index.
    GIVEN non-empty scores WHEN selecting a candidate THEN return argmax.
    """
    if not scores:
        raise ValueError("scores must be non-empty")
    best_i = 0
    best_v = scores[0]
    for i in range(1, len(scores)):
        if scores[i] > best_v:
            best_i = i
            best_v = scores[i]
    return best_i


def distinct_n(token_ids: Sequence[int], n: int) -> float:
    """Fraction of unique n-grams among consecutive n-grams."""
    if n < 1 or len(token_ids) < n:
        return 0.0
    grams = [
        tuple(token_ids[i : i + n]) for i in range(len(token_ids) - n + 1)
    ]
    return len(set(grams)) / len(grams)
