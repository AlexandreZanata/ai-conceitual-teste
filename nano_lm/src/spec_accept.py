"""Speculative verify: accept draft prefix under target/draft probability ratio."""

from __future__ import annotations

from typing import Sequence


def accept_prefix_len(
    draft_probs: Sequence[float],
    target_probs: Sequence[float],
    uniforms: Sequence[float],
) -> int:
    """
    GIVEN aligned draft/target token probs and U(0,1) draws
    WHEN verifying a draft of length γ
    THEN accept while u_i <= min(1, p_i / q_i); stop at first reject.
    Returns accepted count in [0, γ].
    """
    if not (len(draft_probs) == len(target_probs) == len(uniforms)):
        raise ValueError("draft_probs, target_probs, uniforms must align")
    n_ok = 0
    for q, p, u in zip(draft_probs, target_probs, uniforms):
        if q <= 0.0:
            break
        if u > min(1.0, p / q):
            break
        n_ok += 1
    return n_ok


def residual_probs(
    target_probs: Sequence[float], draft_probs: Sequence[float]
) -> list[float]:
    """
    GIVEN vocab target p and draft q at a reject position
    WHEN building the residual distribution
    THEN return max(0, p - q) renormalized (or uniform if mass ~0).
    """
    if len(target_probs) != len(draft_probs):
        raise ValueError("vocab distributions must align")
    raw = [max(0.0, float(p) - float(q)) for p, q in zip(target_probs, draft_probs)]
    mass = sum(raw)
    if mass <= 1e-12:
        n = len(raw)
        return [1.0 / n] * n
    return [x / mass for x in raw]
