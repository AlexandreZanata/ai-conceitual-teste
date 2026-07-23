"""H-PARE: DECK search archives (lp, wall); claim = knee of Pareto front."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from dec_fit_ops import fitness_gene_detail, proxy_fitness_gene
from decode_genes import Gene, clamp_gene, mutate_gene, random_gene
from deck_ops import teacher_forward_budget, wall_saved
from eval_student import load_student_ckpt
from lat_ops import latency_aware_score
from load_model import load_causal_lm
from lofi_ops import top_k_indices
from matrix_common import write_json
from pare_ops import pareto_indices, pick_knee


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_pare(
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
    top_k: int = 1,
    lam: float = 0.15,
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    tok = teacher.tokenizer
    device = teacher.device
    student = load_student_ckpt(student_ckpt, tok, device)
    prompts = _prompts(prompts_path)
    pop = [random_gene(rng) for _ in range(pop_size)]
    arch_lps: list[float] = []
    arch_walls: list[float] = []
    arch_genes: list[Gene] = []
    history: list[dict[str, Any]] = []
    teacher_forwards = 0
    t0 = time.perf_counter()
    for gen in range(generations):
        proxies = [
            proxy_fitness_gene(
                g,
                student=student,
                tok=tok,
                device=device,
                prompts=prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
            )
            for g in pop
        ]
        top = top_k_indices(proxies, top_k)
        scores = [float("-inf")] * pop_size
        for i in top:
            lp, wall = fitness_gene_detail(
                pop[i],
                teacher=teacher,
                student=student,
                prompts=prompts,
                max_new=max_new,
                seed=seed + 2000 * gen + i,
            )
            teacher_forwards += len(prompts)
            scores[i] = latency_aware_score(lp, wall, lam)
            arch_lps.append(lp)
            arch_walls.append(wall)
            arch_genes.append(clamp_gene(pop[i]))
        ranked = sorted(range(pop_size), key=lambda i: scores[i], reverse=True)
        history.append({"gen": gen, "best_score": scores[ranked[0]], "top_k": top})
        parents = [
            pop[i] for i in ranked[: max(1, pop_size // 2)] if scores[i] > float("-inf")
        ]
        if not parents:
            parents = [pop[i] for i in top]
        pop = [mutate_gene(parents[i % len(parents)], rng) for i in range(pop_size)]
    front = pareto_indices(arch_lps, arch_walls)
    if not front:
        raise RuntimeError("H-PARE: empty archive / Pareto front")
    flps = [arch_lps[i] for i in front]
    fwalls = [arch_walls[i] for i in front]
    knee_local = pick_knee(flps, fwalls)
    knee_i = front[knee_local]
    best_gene = arch_genes[knee_i]
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    eval_lp, eval_wall = fitness_gene_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    lofi_b, full_b = teacher_forward_budget(
        pop_size=pop_size,
        generations=generations,
        n_prompts=len(prompts),
        top_k=top_k,
    )
    meta = {
        "hypothesis": "H-PARE",
        "top_k": top_k,
        "lam": lam,
        "best_gene": best_gene,
        "best_fit": arch_lps[knee_i],
        "front_n": len(front),
        "archive_n": len(arch_lps),
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_max_new": hold,
        "teacher_forwards": teacher_forwards,
        "teacher_forward_budget": lofi_b,
        "full_hdec_forwards": full_b,
        "wall_save": wall_saved(lofi_b, full_b),
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
