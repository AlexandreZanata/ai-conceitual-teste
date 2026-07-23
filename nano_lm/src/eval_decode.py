"""Evaluate B2 checkpoint under AR / BoN / speculative decode vs teacher."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Callable

import torch
import yaml

from decode_ar import decode_ar
from decode_bon import decode_bon
from decode_spec import decode_spec
from eval_student import load_student_ckpt, teacher_mean_logprob
from load_model import LoadedModel, load_causal_lm
from scorers import DecodeResult


def _load_prompts(path: Path) -> list[dict[str, Any]]:
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)["prompts"]


def _tokens_per_s(result: DecodeResult) -> float:
    if result.wall_ms <= 0 or not result.token_ids:
        return 0.0
    return len(result.token_ids) / (result.wall_ms / 1000.0)


def score_decode_run(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[dict[str, Any]],
    family: str,
    max_new_tokens: int,
    seed: int,
    temperature: float,
    top_p: float,
    decode_fn: Callable[..., DecodeResult],
    decode_kwargs: dict[str, Any] | None = None,
    label: str,
) -> dict[str, Any]:
    tok = teacher.tokenizer
    device = teacher.device
    kw = dict(decode_kwargs or {})
    scores: list[float] = []
    walls: list[float] = []
    speeds: list[float] = []
    for i, p in enumerate(prompts):
        result = _call_decode(
            family,
            decode_fn,
            student,
            teacher.model,
            tok,
            p["text"],
            device,
            max_new_tokens,
            temperature,
            top_p,
            seed + i,
            kw,
        )
        prompt_ids = tok.encode(p["text"], return_tensors="pt")
        scores.append(
            teacher_mean_logprob(teacher, prompt_ids, list(result.token_ids))
        )
        walls.append(result.wall_ms)
        speeds.append(_tokens_per_s(result))
    return {
        "label": label,
        "family": family,
        "teacher_mean_logprob": sum(scores) / len(scores),
        "mean_wall_ms": sum(walls) / len(walls),
        "mean_tokens_per_s": sum(speeds) / len(speeds),
        "n_prompts": len(prompts),
        "seed": seed,
    }


def _call_decode(
    family: str,
    decode_fn: Callable[..., DecodeResult],
    student: Any,
    teacher_model: Any,
    tok: Any,
    text: str,
    device: torch.device,
    max_new: int,
    temperature: float,
    top_p: float,
    seed: int,
    extra: dict[str, Any],
) -> DecodeResult:
    base = dict(
        tokenizer=tok,
        prompt=text,
        max_new_tokens=max_new,
        temperature=temperature,
        top_p=top_p,
        seed=seed,
        device=device,
        **extra,
    )
    if family == "H-SPEC":
        return decode_fn(student=student, teacher=teacher_model, **base)
    return decode_fn(model=student, **base)


def load_pair(
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    cache_dir: Path,
) -> tuple[LoadedModel, object]:
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    return teacher, student


def eval_decode_ops_for_ckpt(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    max_new_tokens: int,
    seed: int,
    temperature: float = 0.8,
    top_p: float = 0.9,
    draft_len: int = 4,
    bon_n: int = 4,
) -> list[dict[str, Any]]:
    teacher, student = load_pair(
        student_ckpt, teacher_id, tokenizer_id, cache_dir
    )
    prompts = _load_prompts(prompts_path)
    shared = dict(
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new_tokens=max_new_tokens,
        seed=seed,
        temperature=temperature,
        top_p=top_p,
    )
    return [
        score_decode_run(
            family="B3",
            decode_fn=decode_ar,
            label=f"B3_{student_ckpt.stem}",
            **shared,
        ),
        score_decode_run(
            family="B4",
            decode_fn=decode_bon,
            decode_kwargs={"n": bon_n},
            label=f"B4_{student_ckpt.stem}",
            **shared,
        ),
        score_decode_run(
            family="H-SPEC",
            decode_fn=decode_spec,
            decode_kwargs={"draft_len": draft_len},
            label=f"HSPEC_{student_ckpt.stem}",
            **shared,
        ),
    ]
