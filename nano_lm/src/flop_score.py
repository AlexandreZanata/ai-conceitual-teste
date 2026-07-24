"""Score decode runs with wall_ms + tokens/s + estimated GFLOPs."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import yaml

from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from load_model import LoadedModel
from scorers import DecodeResult
from student_model import count_params


def load_prompts(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)["prompts"]


def score_with_flops(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[dict[str, Any]],
    family: str,
    label: str,
    seed: int,
    max_new_tokens: int,
    decode_fn: Callable[..., DecodeResult],
    decode_kwargs: dict[str, Any] | None = None,
) -> dict[str, Any]:
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    kw = dict(decode_kwargs or {})
    scores: list[float] = []
    walls: list[float] = []
    speeds: list[float] = []
    gflops: list[float] = []
    evals: list[float] = []
    for i, p in enumerate(prompts):
        result = decode_fn(
            model=student,
            tokenizer=tok,
            prompt=p["text"],
            max_new_tokens=max_new_tokens,
            seed=seed + i,
            device=device,
            **kw,
        )
        prompt_ids = tok.encode(p["text"], return_tensors="pt")
        scores.append(
            teacher_mean_logprob(teacher, prompt_ids, list(result.token_ids))
        )
        walls.append(result.wall_ms)
        n_new = len(result.token_ids)
        speeds.append(tokens_per_s(n_new=n_new, wall_ms=result.wall_ms))
        fl = est_decode_flops(
            n_params=n_params,
            prompt_len=int(prompt_ids.shape[1]),
            n_new=n_new,
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(fl))
        evals.append(float(result.token_evals))
    n = max(len(scores), 1)
    return {
        "label": label,
        "family": family,
        "teacher_mean_logprob": sum(scores) / n,
        "mean_wall_ms": sum(walls) / n,
        "mean_tokens_per_s": sum(speeds) / n,
        "mean_est_gflops": sum(gflops) / n,
        "mean_token_evals": sum(evals) / n,
        "n_params": int(n_params),
        "n_prompts": len(prompts),
        "seed": seed,
    }
