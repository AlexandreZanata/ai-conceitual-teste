"""H-REP: search rep_penalty / no_repeat_ngram under frozen H-EARLY tip."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from eval_student import load_student_ckpt
from lat_ops import latency_aware_score
from load_model import load_causal_lm
from matrix_common import write_json
from rep_fit import fitness_rep_detail
from rep_ops import clamp_rep_gene, mutate_rep_gene, random_rep_gene


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_rep(
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
    pop = [random_rep_gene(rng, early_gene) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_score = float("-inf")
    t0 = time.perf_counter()
    for gen in range(generations):
        details = [
            fitness_rep_detail(
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
        scores = [latency_aware_score(lp, w, lam) for lp, w, _gf in details]
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        history.append(
            {
                "gen": gen,
                "best_score": scores[ranked[0]],
                "best_rep_penalty": pop[ranked[0]]["rep_penalty"],
                "best_ngram": pop[ranked[0]]["no_repeat_ngram"],
            }
        )
        if scores[ranked[0]] > best_score:
            best_score = scores[ranked[0]]
            best_gene = clamp_rep_gene(pop[ranked[0]], early_gene)
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [
            mutate_rep_gene(parents[i % len(parents)], rng, early_gene)
            for i in range(pop_size)
        ]
    eval_lp, eval_wall, eval_gf = fitness_rep_detail(
        best_gene,
        early_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 9001,
    )
    meta = {
        "hypothesis": "H-REP",
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
