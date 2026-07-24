"""Score STAG tip vs H-TIE student (AR decode + params + FLOPs)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from decode_ar import decode_ar
from eval_student import load_student_ckpt, teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from student_model import build_student, count_params
from tie_student import build_tie_student


def flop_param_count(model: object) -> int:
    """
    GIVEN a student
    WHEN estimating decode FLOPs
    THEN use untied arch size if blocks are shared (depth still paid).
    """
    blocks = list(model.transformer.h)
    n_unique = len({id(b) for b in blocks})
    if n_unique < len(blocks):
        return count_params(build_student())
    return count_params(model)


def score_ar_ckpt(
    *,
    ckpt: Path,
    teacher: LoadedModel,
    prompts: list[str],
    max_new: int,
    seed: int,
    decode_seed: int,
    build_fn,
    family: str,
    label: str,
) -> dict[str, Any]:
    student = load_student_ckpt(
        ckpt, teacher.tokenizer, teacher.device, build_fn=build_fn
    )
    n_params = count_params(student)
    n_flop = flop_param_count(student)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_ar(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=0.8,
            top_p=0.9,
            seed=decode_seed + i,
            device=device,
        )
        walls.append(result.wall_ms)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        fl = est_decode_flops(
            n_params=n_flop,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(fl))
    n = max(len(scores), 1)
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": sum(scores) / n,
        "mean_wall_ms": sum(walls) / n,
        "mean_est_gflops": sum(gflops) / n,
        "n_params": int(n_params),
        "n_prompts": len(prompts),
        "seed": seed,
        "build": build_fn.__name__,
    }
