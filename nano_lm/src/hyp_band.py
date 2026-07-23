"""H-BAND: UCB1 over fixed gene arms (no mutate pop)."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from band_ops import ucb1_select
from dec_fit_ops import fitness_gene
from decode_genes import clamp_gene, random_gene
from eval_student import load_student_ckpt
from load_model import load_causal_lm
from matrix_common import write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_band(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    n_arms: int,
    n_pulls: int,
    max_new: int,
    seed: int,
    out_meta: Path,
    eval_max_new: int | None = None,
    ucb_c: float = 1.41421356237,
) -> dict[str, Any]:
    if min(n_arms, n_pulls) < 1:
        raise ValueError("run_h_band: n_arms and n_pulls must be >= 1")
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    tok = teacher.tokenizer
    device = teacher.device
    student = load_student_ckpt(student_ckpt, tok, device)
    prompts = _prompts(prompts_path)
    arms = [random_gene(rng) for _ in range(n_arms)]
    means = [0.0] * n_arms
    counts = [0] * n_arms
    history: list[dict[str, Any]] = []
    best_gene = arms[0]
    best_fit = float("-inf")
    teacher_forwards = 0
    t0 = time.perf_counter()
    for t in range(1, n_pulls + 1):
        arm = ucb1_select(means, counts, total_pulls=t, c=ucb_c)
        fit = fitness_gene(
            arms[arm],
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=max_new,
            seed=seed + 1000 * t + arm,
        )
        teacher_forwards += len(prompts)
        counts[arm] += 1
        means[arm] += (fit - means[arm]) / float(counts[arm])
        history.append({"pull": t, "arm": arm, "fit": fit})
        if fit > best_fit:
            best_fit = fit
            best_gene = clamp_gene(arms[arm])
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    eval_fit = fitness_gene(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": "H-BAND",
        "n_arms": n_arms,
        "n_pulls": n_pulls,
        "ucb_c": ucb_c,
        "best_gene": best_gene,
        "best_fit": best_fit,
        "eval_fit": eval_fit,
        "eval_max_new": hold,
        "teacher_forwards": teacher_forwards,
        "arm_counts": counts,
        "arm_means": means,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
