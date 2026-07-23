"""H-STACK: evolve early genes → elite mixture claim (EARLY × DECM)."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from early_fit import fitness_early_detail
from early_ops import clamp_early_gene, mutate_early_gene, random_early_gene
from eval_student import load_student_ckpt
from lat2_ops import MIN_LAM
from lat_ops import latency_aware_score
from load_model import load_causal_lm
from matrix_common import write_json
from stack_ops import MIX_M
from stack_search import claim_early_mixture, elite_early_mixture


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_stack(
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
    mix_m: int = MIX_M,
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
    pop = [random_early_gene(rng) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for gen in range(generations):
        details = [
            fitness_early_detail(
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
        history.append({"gen": gen, "best_score": scores[ranked[0]]})
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [
            mutate_early_gene(parents[i % len(parents)], rng) for i in range(pop_size)
        ]
    details = [
        fitness_early_detail(
            g,
            teacher=teacher,
            student=student,
            prompts=fit_prompts,
            max_new=max_new,
            seed=seed + 5000,
        )
        for g in pop
    ]
    scores = [latency_aware_score(lp, w, lam) for lp, w in details]
    mixture = elite_early_mixture(pop, scores, m=mix_m)
    best_gene = clamp_early_gene(mixture[0])
    mix_lp, mix_wall, picks = claim_early_mixture(
        mixture,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    early_lp, early_wall = fitness_early_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 8888,
    )
    meta = {
        "hypothesis": "H-STACK",
        "lam": lam,
        "mix_m": mix_m,
        "mixture": mixture,
        "best_gene": best_gene,
        "best_fit": float(details[scores.index(max(scores))][0]),
        "eval_fit": mix_lp,
        "eval_wall_ms": mix_wall,
        "early_eval_fit": early_lp,
        "early_eval_wall_ms": early_wall,
        "picks": picks,
        "eval_max_new": hold,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
