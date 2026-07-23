"""H-CLIP: logit-clipped KD helpers; decide vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

from train_ce import ce_loss

__all__ = ["DEFAULT_CLIP", "clip_logits", "clip_kd_loss", "decide_hclip"]

DEFAULT_CLIP = 5.0


def clip_logits(logits: torch.Tensor, clip: float) -> torch.Tensor:
    """
    GIVEN logits and clip ≥ 0
    WHEN soft-clamping
    THEN return logits.clamp(-clip, clip); clip=0 is identity.
    """
    c = float(clip)
    if c < 0.0:
        raise ValueError("clip_logits: clip must be >= 0")
    if c == 0.0:
        return logits
    return logits.clamp(-c, c)


def clip_kd_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    ids: torch.Tensor,
    *,
    temperature: float,
    alpha: float,
    clip: float = DEFAULT_CLIP,
) -> torch.Tensor:
    """
    GIVEN student/teacher logits
    WHEN forming clipped KD
    THEN CE + T²·KL after clamping both logit tensors to [-clip, clip].
    """
    t = max(float(temperature), 1e-6)
    s = clip_logits(student_logits[:, :-1, :].float(), clip) / t
    tea = clip_logits(teacher_logits[:, :-1, :].float(), clip) / t
    log_p = F.log_softmax(s, dim=-1)
    q = F.softmax(tea, dim=-1)
    kl = F.kl_div(log_p, q, reduction="batchmean") * (t * t)
    return float(alpha) * ce_loss(student_logits, ids) + (1.0 - float(alpha)) * kl


def decide_hclip(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-CLIP vs B2
    WHEN deciding
    THEN PROMOTE iff teacher_lp > B2; else KILL.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (≤ B2)"
