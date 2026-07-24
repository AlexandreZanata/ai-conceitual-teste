"""H-TRIM: FLOP-aware search with tip n frozen; other knobs free."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from earf_ops import flop_aware_score
from eval_student import load_student_ckpt
from load_model import load_causal_lm
from matrix_common import write_json
from poolf_fit import fitness_poolf_detail
from trim_ops import clamp_trim_gene, mutate_trim_gene, seed_trim_from_tip


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _init_pop(rng: random.Random, tip: dict[str, Any], pop_size: int) -> list[dict]:
    frozen_n = int(tip["n"])
    pop = [clamp_trim_gene(tip, frozen_n)]
    while len(pop) < pop_size:
        pop.append(seed_trim_from_tip(tip, rng))
    return pop


def run_h_trim(
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
    tip_gene: dict[str, Any],
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
    frozen_n = int(tip_gene["n"])

    def clamp_fn(g: dict[str, Any]) -> dict[str, Any]:
        return clamp_trim_gene(g, frozen_n)

    pop = _init_pop(rng, tip_gene, pop_size)
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_score = float("-inf")
    best_lp = float("-inf")
    best_gf = float("inf")
    t0 = time.perf_counter()
    for gen in range(generations):
        details = [
            fitness_poolf_detail(
                g,
                teacher=teacher,
                student=student,
                prompts=fit_prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
                clamp_fn=clamp_fn,
            )
            for g in pop
        ]
        scores = [flop_aware_score(lp, gf, lam) for lp, _w, gf in details]
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        history.append(
            {
                "gen": gen,
                "best_score": scores[ranked[0]],
                "best_n": frozen_n,
                "best_gflops": details[ranked[0]][2],
            }
        )
        if scores[ranked[0]] > best_score:
            best_score = scores[ranked[0]]
            best_lp = details[ranked[0]][0]
            best_gf = details[ranked[0]][2]
            best_gene = clamp_trim_gene(pop[ranked[0]], frozen_n)
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [
            mutate_trim_gene(parents[i % len(parents)], frozen_n, rng)
            for i in range(pop_size)
        ]
    eval_lp, eval_wall, eval_gf = fitness_poolf_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
        clamp_fn=clamp_fn,
    )
    meta = {
        "hypothesis": "H-TRIM",
        "frozen_n": frozen_n,
        "lam": lam,
        "best_gene": best_gene,
        "best_score": best_score,
        "best_fit": best_lp,
        "best_gflops": best_gf,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_est_gflops": eval_gf,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
