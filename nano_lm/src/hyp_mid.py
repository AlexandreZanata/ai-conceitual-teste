"""H-MID: mid min_new + tip warm-start; FLOP-aware early search."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from earf_fit import fitness_earf_detail
from earf_ops import flop_aware_score
from eval_student import load_student_ckpt
from lat2_ops import MIN_LAM
from load_model import load_causal_lm
from matrix_common import write_json
from mid_ops import (
    clamp_mid_gene,
    mutate_mid_gene,
    random_mid_gene,
    seed_mid_from_tip,
)


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _init_pop(
    rng: random.Random, tip: dict[str, Any] | None, pop_size: int
) -> list[dict[str, Any]]:
    if tip is None:
        return [random_mid_gene(rng) for _ in range(pop_size)]
    warm = max(1, pop_size // 2)
    pop = [seed_mid_from_tip(tip, rng) for _ in range(warm)]
    while len(pop) < pop_size:
        pop.append(random_mid_gene(rng))
    return pop


def run_h_mid(
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
    tip_gene: dict[str, Any] | None = None,
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
    pop = _init_pop(rng, tip_gene, pop_size)
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_score = float("-inf")
    best_lp = float("-inf")
    best_gf = float("inf")
    t0 = time.perf_counter()
    for gen in range(generations):
        details = [
            fitness_earf_detail(
                g,
                teacher=teacher,
                student=student,
                prompts=fit_prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
                clamp_fn=clamp_mid_gene,
            )
            for g in pop
        ]
        scores = [flop_aware_score(lp, gf, lam) for lp, _w, gf in details]
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        history.append(
            {
                "gen": gen,
                "best_score": scores[ranked[0]],
                "best_min_new": pop[ranked[0]]["min_new"],
                "best_gflops": details[ranked[0]][2],
            }
        )
        if scores[ranked[0]] > best_score:
            best_score = scores[ranked[0]]
            best_lp = details[ranked[0]][0]
            best_gf = details[ranked[0]][2]
            best_gene = clamp_mid_gene(pop[ranked[0]])
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [
            mutate_mid_gene(parents[i % len(parents)], rng) for i in range(pop_size)
        ]
    eval_lp, eval_wall, eval_gf = fitness_earf_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
        clamp_fn=clamp_mid_gene,
    )
    meta = {
        "hypothesis": "H-MID",
        "lam": lam,
        "best_gene": best_gene,
        "best_score": best_score,
        "best_fit": best_lp,
        "best_gflops": best_gf,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_est_gflops": eval_gf,
        "eval_max_new": hold,
        "warm_start": tip_gene is not None,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
