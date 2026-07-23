"""Evaluate student completions under frozen teacher (primary metric)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch
import yaml

from decode_ar import decode_ar
from load_model import LoadedModel, load_causal_lm
from scorers import mean_logprob
from student_model import build_student


def load_student_ckpt(
    path: Path, tokenizer, device: torch.device
) -> object:
    student = build_student(len(tokenizer)).to(device)
    blob = torch.load(path, map_location=device, weights_only=True)
    student.load_state_dict(blob["model"])
    student.eval()
    return student


def teacher_mean_logprob(
    teacher: LoadedModel, prompt_ids: torch.Tensor, cont_ids: list[int]
) -> float:
    """Length-normalized logprob of continuation tokens under teacher."""
    if not cont_ids:
        return float("-inf")
    device = teacher.device
    ids = prompt_ids.to(device)
    lps: list[float] = []
    with torch.no_grad():
        for tok in cont_ids:
            out = teacher.model(ids)
            logits = out.logits[:, -1, :].float()
            logp = torch.log_softmax(logits, dim=-1)[0, tok]
            lps.append(float(logp.item()))
            nxt = torch.tensor([[tok]], device=device, dtype=ids.dtype)
            ids = torch.cat([ids, nxt], dim=1)
    return mean_logprob(lps)


def eval_student_vs_teacher(
    *,
    student_ckpt: Path | None,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    max_new_tokens: int,
    seed: int,
    temperature: float,
    top_p: float,
) -> dict[str, Any]:
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    tok = teacher.tokenizer
    device = teacher.device
    if student_ckpt is None:
        student = build_student(len(tok)).to(device)
        student.eval()
        label = "B0"
    else:
        student = load_student_ckpt(student_ckpt, tok, device)
        label = student_ckpt.stem
    with prompts_path.open(encoding="utf-8") as f:
        prompts = yaml.safe_load(f)["prompts"]
    scores: list[float] = []
    walls: list[float] = []
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
        score = teacher_mean_logprob(teacher, prompt_ids, list(result.token_ids))
        scores.append(score)
        walls.append(result.wall_ms)
    return {
        "label": label,
        "teacher_mean_logprob": sum(scores) / len(scores),
        "mean_wall_ms": sum(walls) / len(walls),
        "n_prompts": len(prompts),
        "seed": seed,
    }
