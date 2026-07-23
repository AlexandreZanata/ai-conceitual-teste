"""H-NGRE: stack tip EARLY gene × tip NGRAM size; claim vs max tip."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import yaml

from eval_student import load_student_ckpt
from load_model import load_causal_lm
from matrix_common import write_json
from ngre_fit import fitness_ngre_detail


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_ngre(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    max_new: int,
    seed: int,
    out_meta: Path,
    early_train: Path,
    ngram_train: Path,
    eval_prompts_path: Path | None = None,
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    early = json.loads(early_train.read_text(encoding="utf-8"))
    ngram = json.loads(ngram_train.read_text(encoding="utf-8"))
    gene = early["best_gene"]
    n_size = int(ngram["best_ngram_size"])
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    t0 = time.perf_counter()
    eval_lp, eval_wall = fitness_ngre_detail(
        gene,
        n_size,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": "H-NGRE",
        "early_gene": gene,
        "ngram_size": n_size,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_max_new": hold,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
        "early_train": str(early_train),
        "ngram_train": str(ngram_train),
    }
    write_json(out_meta, meta)
    return meta
