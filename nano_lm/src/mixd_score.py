"""Score H-MIXD: student causal PPL on hold-out prog texts."""

from __future__ import annotations

import math
from typing import Sequence

import torch

from eval_student import load_student_ckpt
from train_ce import ce_loss

__all__ = ["student_mean_ppl"]


def student_mean_ppl(
    ckpt,
    tok: object,
    texts: Sequence[str],
    *,
    device: torch.device,
    seq_len: int,
) -> float:
    """
    GIVEN student checkpoint + hold-out texts
    WHEN measuring shifted CE
    THEN return exp(mean NLL) perplexity.
    """
    from pathlib import Path

    student = load_student_ckpt(Path(ckpt), tok, device)
    nlls: list[float] = []
    with torch.no_grad():
        for text in texts:
            ids = tok.encode(text, add_special_tokens=False)
            if len(ids) < 2:
                continue
            chunk = ids[: int(seq_len)]
            if len(chunk) < 2:
                continue
            t = torch.tensor([chunk], dtype=torch.long, device=device)
            loss = ce_loss(student(t).logits, t)
            nlls.append(float(loss.item()))
    if not nlls:
        raise ValueError("student_mean_ppl: no scored texts")
    return math.exp(sum(nlls) / len(nlls))
