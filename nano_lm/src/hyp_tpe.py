"""H-TPE: evolve typ_mass + T/top_p; dual gate vs H-TYP."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from eval_student import load_student_ckpt
from lat2_ops import MIN_LAM
from lat_ops import latency_aware_score
from load_model import load_causal_lm
from matrix_common import write_json
from tpe_fit import fitness_tpe_detail
from tpe_ops import clamp_tpe_gene, mutate_tpe_gene, random_tpe_gene


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_tpe(
    *,
    student_ckpt: Path,
    teacher_id: str,
    tokenizer_id: str,
    prompts_path: Path,
    cache_dir: Path,
    pop_size: int,
    generations: int,
    max_new: int,
    seed: int,
    out_meta: Path,
    lam: float = MIN_LAM,
    eval_prompts_path: Path | None = None,
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    fit_prompts = _prompts(prompts_path)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    pop = [random_tpe_gene(rng) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_score = float("-inf")
    best_lp = float("-inf")
    t0 = time.perf_counter()
    for gen in range(generations):
        details = [
            fitness_tpe_detail(
                g,
                teacher=teacher,
                student=student,
                prompts=fit_prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
            )
            for g in pop
        ]
        scores = [latency_aware_score(lp, w, lam) for lp, w in details]
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        history.append(
            {
                "gen": gen,
                "best_score": scores[ranked[0]],
                "best_typ_mass": pop[ranked[0]]["typ_mass"],
            }
        )
        if scores[ranked[0]] > best_score:
            best_score = scores[ranked[0]]
            best_lp = details[ranked[0]][0]
            best_gene = clamp_tpe_gene(pop[ranked[0]])
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [
            mutate_tpe_gene(parents[i % len(parents)], rng) for i in range(pop_size)
        ]
    eval_lp, eval_wall = fitness_tpe_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": "H-TPE",
        "lam": lam,
        "best_gene": best_gene,
        "best_score": best_score,
        "best_fit": best_lp,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_max_new": hold,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
