"""In-memory val teacher_lp for H-STEP early-stop (fit prompts)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import yaml

from decode_ar import decode_ar
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def val_teacher_lp(
    student: Any,
    teacher: LoadedModel,
    *,
    prompts_path: Path,
    max_new_tokens: int,
    seed: int,
    temperature: float = 0.8,
    top_p: float = 0.9,
) -> float:
    """
    GIVEN loaded student + teacher and holdout prompts
    WHEN scoring student completions
    THEN return mean length-normalized teacher log-prob.
    """
    tok = teacher.tokenizer
    device = teacher.device
    with prompts_path.open(encoding="utf-8") as f:
        prompts = yaml.safe_load(f)["prompts"]
    scores: list[float] = []
    was_training = student.training
    student.eval()
    try:
        for i, p in enumerate(prompts):
            result = decode_ar(
                student,
                tok,
                p["text"],
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                top_p=top_p,
                seed=seed + i,
                device=device,
            )
            prompt_ids = tok.encode(p["text"], return_tensors="pt")
            scores.append(
                teacher_mean_logprob(teacher, prompt_ids, list(result.token_ids))
            )
    finally:
        if was_training:
            student.train()
    return sum(scores) / max(len(scores), 1)
