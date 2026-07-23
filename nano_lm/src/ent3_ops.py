"""H-ENT3 helpers: maximize TV (disagreement) + mix logits + decision."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

from ent_ops import heads_collapsed

CHAOS_TV = 0.9
TV_FLOOR = 0.02


def soft_tv(logits_a: torch.Tensor, logits_b: torch.Tensor) -> torch.Tensor:
    """
    GIVEN dual-head logits
    WHEN measuring separation
    THEN return mean total-variation (differentiable).
    """
    a = F.softmax(logits_a[:, :-1, :].float(), dim=-1)
    b = F.softmax(logits_b[:, :-1, :].float(), dim=-1)
    return 0.5 * (a - b).abs().sum(dim=-1).mean()


def mix_logits(logits_a: torch.Tensor, logits_b: torch.Tensor) -> torch.Tensor:
    """Average dual-head logits for teacher KD on the mixture."""
    return 0.5 * (logits_a + logits_b)


def mode_chaos(tv: float, *, ceiling: float = CHAOS_TV) -> bool:
    """True when mean TV exceeds chaos ceiling (heads too adversarial)."""
    if ceiling <= 0.0:
        raise ValueError("mode_chaos: ceiling must be > 0")
    return float(tv) > ceiling


def decide_hent3(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-ENT3 stats
    WHEN deciding
    THEN KILL on collapse or mode chaos; else require beat B2.
    """
    if float(s.get("collapsed", 0.0)) > 0.0:
        return "KILL (collapsed)"
    if float(s.get("mode_chaos", 0.0)) > 0.0:
        return "KILL (mode chaos)"
    b2 = stats.get("B2", {}).get("mean_lp")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2) + 1e-6:
        return "PROMOTE (beats B2, heads distinct)"
    return "KILL / hold (≤ B2)"


def collapse_or_chaos(tv: float, *, floor: float = TV_FLOOR, ceiling: float = CHAOS_TV) -> tuple[bool, bool]:
    """Return (heads_collapsed, mode_chaos) for a mean TV."""
    return heads_collapsed(tv, floor=floor), mode_chaos(tv, ceiling=ceiling)
