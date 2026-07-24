"""H-PROX: warm-start POOL search ranked by student CE only; teacher claim."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from dec_fit_ops import fitness_gene_detail, proxy_ce_fitness_gene
from decode_genes import Gene, clamp_gene, mutate_gene, random_gene
from eval_student import load_student_ckpt
from load_model import load_causal_lm
from matrix_common import write_json
from pool_ops import warm_start_pop


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_prox(
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
    lam: float = 0.15,
    eval_prompts_path: Path | None = None,
    eval_max_new: int | None = None,
    init_genes: list[Gene] | None = None,
    hypothesis: str = "H-PROX",
) -> dict[str, Any]:
    del lam  # kept for call-site parity with H-POOL; unused without teacher fit
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    tok = teacher.tokenizer
    device = teacher.device
    student = load_student_ckpt(student_ckpt, tok, device)
    fit_prompts = _prompts(prompts_path)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    if init_genes:
        pop = warm_start_pop(init_genes, pop_size, rng)
    else:
        pop = [random_gene(rng) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_proxy = float("-inf")
    t0 = time.perf_counter()
    for gen in range(generations):
        proxies = [
            proxy_ce_fitness_gene(
                g,
                student=student,
                tok=tok,
                device=device,
                prompts=fit_prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
            )
            for g in pop
        ]
        ranked = sorted(range(pop_size), key=lambda i: proxies[i], reverse=True)
        history.append({"gen": gen, "best_proxy": proxies[ranked[0]]})
        if proxies[ranked[0]] > best_proxy:
            best_proxy = proxies[ranked[0]]
            best_gene = clamp_gene(pop[ranked[0]])
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [mutate_gene(parents[i % len(parents)], rng) for i in range(pop_size)]
    search_wall_s = time.perf_counter() - t0
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    eval_lp, eval_wall = fitness_gene_detail(
        best_gene,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": hypothesis,
        "warm_start": bool(init_genes),
        "proxy": "ce",
        "best_gene": best_gene,
        "best_proxy": best_proxy,
        "best_fit": best_proxy,
        "eval_fit": eval_lp,
        "eval_wall_ms": eval_wall,
        "eval_max_new": hold,
        "teacher_forwards": 0,
        "search_wall_s": search_wall_s,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
