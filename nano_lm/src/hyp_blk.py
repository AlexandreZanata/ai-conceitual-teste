"""Score H-BLK block-parallel decode (+ optional B3 AR) on a student ckpt."""

from __future__ import annotations

import time
from pathlib import Path
from typing import Any

import yaml

from decode_ar import decode_ar
from decode_block import decode_block
from eval_student import load_student_ckpt, teacher_mean_logprob
from load_model import load_causal_lm
from matrix_common import write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _score(
    *,
    decode_fn,
    decode_kw: dict[str, Any],
    teacher,
    student,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, int]:
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    evals = 0
    for i, text in enumerate(prompts):
        result = decode_fn(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=0.8,
            top_p=0.9,
            seed=seed + i,
            device=device,
            **decode_kw,
        )
        walls.append(float(result.wall_ms))
        evals += int(result.token_evals)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls), evals


def run_h_blk(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    max_new: int,
    seed: int,
    out_meta: Path,
    block_size: int = 4,
) -> dict[str, Any]:
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    prompts = _prompts(prompts_path)
    t0 = time.perf_counter()
    blk_lp, blk_wall, blk_evals = _score(
        decode_fn=decode_block,
        decode_kw={"block_size": block_size},
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 100,
    )
    b3_lp, b3_wall, b3_evals = _score(
        decode_fn=decode_ar,
        decode_kw={},
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 200,
    )
    meta = {
        "hypothesis": "H-BLK",
        "block_size": block_size,
        "eval_fit": blk_lp,
        "eval_wall_ms": blk_wall,
        "token_evals": blk_evals,
        "b3_eval_fit": b3_lp,
        "b3_eval_wall_ms": b3_wall,
        "b3_token_evals": b3_evals,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
