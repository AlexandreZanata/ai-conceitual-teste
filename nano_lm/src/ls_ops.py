"""H-LS: label-smoothed KD helpers; decide vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

from train_ce import ce_loss

__all__ = ["DEFAULT_EPS", "smooth_kd_loss", "decide_hls"]

DEFAULT_EPS = 0.1


def smooth_kd_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    ids: torch.Tensor,
    *,
    temperature: float,
    alpha: float,
    eps: float = DEFAULT_EPS,
) -> torch.Tensor:
    """
    GIVEN student/teacher logits and eps in [0,1)
    WHEN forming label-smoothed KD
    THEN CE + T²·KL(student ‖ (1−ε)·teacher + ε/V).
    """
    e = float(eps)
    if not (0.0 <= e < 1.0):
        raise ValueError("smooth_kd_loss: eps must be in [0,1)")
    t = max(float(temperature), 1e-6)
    s = student_logits[:, :-1, :].float() / t
    tea = teacher_logits[:, :-1, :].float() / t
    v = float(tea.shape[-1])
    log_p = F.log_softmax(s, dim=-1)
    q = F.softmax(tea, dim=-1)
    q = (1.0 - e) * q + e / v
    kl = F.kl_div(log_p, q, reduction="batchmean") * (t * t)
    return float(alpha) * ce_loss(student_logits, ids) + (1.0 - float(alpha)) * kl


def decide_hls(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-LS vs B2
    WHEN deciding
    THEN PROMOTE iff teacher_lp > B2; else KILL.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (≤ B2)"
