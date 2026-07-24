"""H-ALT: search alt_period / start_shallow under frozen H-EARLY tip."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from alt_fit import fitness_alt_detail
from alt_ops import clamp_alt_gene, mutate_alt_gene, random_alt_gene
from eval_student import load_student_ckpt
from lay_ops import flop_aware_score
from load_model import load_causal_lm
from matrix_common import write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_alt(
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
    early_gene: dict[str, Any],
    out_meta: Path,
    lam: float = 0.4,
    eval_max_new: int | None = None,
    eval_prompts_path: Path | None = None,
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
    pop = [random_alt_gene(rng, early_gene) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_score = float("-inf")
    t0 = time.perf_counter()
    for gen in range(generations):
        details = [
            fitness_alt_detail(
                g,
                early_gene,
                teacher=teacher,
                student=student,
                prompts=fit_prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
            )
            for g in pop
        ]
        scores = [flop_aware_score(lp, gf, lam) for lp, _w, gf in details]
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        history.append(
            {
                "gen": gen,
                "best_score": scores[ranked[0]],
                "best_alt_period": pop[ranked[0]]["alt_period"],
                "best_start_shallow": pop[ranked[0]]["start_shallow"],
            }
        )
        if scores[ranked[0]] > best_score:
            best_score = scores[ranked[0]]
            best_gene = clamp_alt_gene(pop[ranked[0]], early_gene)
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [
            mutate_alt_gene(parents[i % len(parents)], rng, early_gene)
            for i in range(pop_size)
        ]
    eval_lp, eval_wall, eval_gf = fitness_alt_detail(
        best_gene,
        early_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 9001,
    )
    meta = {
        "hypothesis": "H-ALT",
        "best_gene": best_gene,
        "best_score": best_score,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_gflops": eval_gf,
        "lam": lam,
        "history": history,
        "wall_s": time.perf_counter() - t0,
    }
    write_json(out_meta, meta)
    return meta
