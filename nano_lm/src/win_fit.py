"""Score STAG tip vs H-WIN student (AR decode + window-scaled FLOPs)."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

from decode_ar import decode_ar
from eval_student import load_student_ckpt, teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from student_model import count_params
from win_ops import DEFAULT_WINDOW, scale_flops_for_window


def score_ar_win(
    *,
    ckpt: Path,
    teacher: LoadedModel,
    prompts: list[str],
    max_new: int,
    seed: int,
    decode_seed: int,
    build_fn: Callable[..., object],
    family: str,
    label: str,
    window: int | None = None,
) -> dict[str, Any]:
    """
    GIVEN ckpt + build_fn
    WHEN AR scoring
    THEN return lp/wall/gflops; windowed models scale attn FLOPs.
    """
    student = load_student_ckpt(
        ckpt, teacher.tokenizer, teacher.device, build_fn=build_fn
    )
    n_params = count_params(student)
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
        prompt_len = int(ids.shape[1])
        n_new = len(result.token_ids)
        full = est_decode_flops(
            n_params=n_params,
            prompt_len=prompt_len,
            n_new=n_new,
            token_evals=result.token_evals,
        )
        seq = prompt_len + max(n_new, 1)
        if window is None:
            scaled = full
        else:
            scaled = scale_flops_for_window(
                full, seq_len=seq, window=int(window)
            )
        gflops.append(to_gflops(scaled))
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
        "window": int(window) if window is not None else DEFAULT_WINDOW,
        "build": getattr(build_fn, "__name__", "build"),
    }
