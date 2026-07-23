"""H-TKD: top-k sparse KD helpers; decide vs B2."""

from __future__ import annotations

from typing import Mapping

import torch
import torch.nn.functional as F

from train_ce import ce_loss

__all__ = ["DEFAULT_K", "topk_kd_loss", "decide_htkd"]

DEFAULT_K = 32


def topk_kd_loss(
    student_logits: torch.Tensor,
    teacher_logits: torch.Tensor,
    ids: torch.Tensor,
    *,
    temperature: float,
    alpha: float,
    k: int = DEFAULT_K,
) -> torch.Tensor:
    """
    GIVEN student/teacher logits and top-k
    WHEN forming sparse KD
    THEN CE + T²·KL over teacher top-k support only (renormalized).
    """
    if int(k) < 1:
        raise ValueError("topk_kd_loss: k must be >= 1")
    t = max(float(temperature), 1e-6)
    s = student_logits[:, :-1, :].float() / t
    tea = teacher_logits[:, :-1, :].float() / t
    k_eff = min(int(k), tea.shape[-1])
    topv, topi = tea.topk(k_eff, dim=-1)
    log_p = F.log_softmax(s.gather(-1, topi), dim=-1)
    q = F.softmax(topv, dim=-1)
    kl = F.kl_div(log_p, q, reduction="batchmean") * (t * t)
    return float(alpha) * ce_loss(student_logits, ids) + (1.0 - float(alpha)) * kl


def decide_htkd(
    s: Mapping[str, float], stats: Mapping[str, Mapping[str, float]]
) -> str:
    """
    GIVEN H-TKD vs B2
    WHEN deciding
    THEN PROMOTE iff teacher_lp > B2; else KILL.
    """
    b2 = stats.get("B2")
    if b2 is None:
        return "needs B2 control"
    if float(s["mean_lp"]) > float(b2["mean_lp"]) + 1e-6:
        return "PROMOTE (beats B2)"
    return "KILL (≤ B2)"
