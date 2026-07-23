"""H-DEB: dual-student pick helpers; decide vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

__all__ = ["soft_kl", "teacher_pick", "peer_kl", "decide_hdeb"]


def soft_kl(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    *,
    temperature: float = 2.0,
) -> torch.Tensor:
    """
    GIVEN student/teacher logits
    WHEN measuring soft KL(student ‖ teacher) on shifted tokens
    THEN return a scalar batchmean * T² (lower is closer to teacher).
    """
    t = max(float(temperature), 1e-6)
    s = student_logits[:, :-1, :].float() / t
    tea = teacher_logits[:, :-1, :].float() / t
    log_p = F.log_softmax(s, dim=-1)
    q = F.softmax(tea, dim=-1)
    return F.kl_div(log_p, q, reduction="batchmean") * (t * t)


def teacher_pick(score_a: float, score_b: float) -> int:
    """
    GIVEN two teacher-proximity scores (lower better)
    WHEN picking a winner
    THEN return 0 if a <= b else 1 (ties keep A).
    """
    return 0 if float(score_a) <= float(score_b) else 1


def peer_kl(
    loser_logits: torch.Tensor,
    winner_logits: torch.Tensor,
    *,
    temperature: float = 2.0,
) -> torch.Tensor:
    """KL(loser ‖ winner) soft targets (winner detached by caller)."""
    return soft_kl(loser_logits, winner_logits, temperature=temperature)


def decide_hdeb(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-DEB vs B2
    WHEN deciding
    THEN PROMOTE iff teacher_lp > B2; else KILL.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (≤ B2)"
