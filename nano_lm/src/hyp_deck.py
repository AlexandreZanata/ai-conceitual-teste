"""H-DECK: cheap student proxy ranks genes; teacher rescores top-k only."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from dec_fit_ops import fitness_gene, proxy_ce_fitness_gene, proxy_fitness_gene
from decode_genes import clamp_gene, mutate_gene, random_gene
from deck_ops import teacher_forward_budget, wall_saved
from eval_student import load_student_ckpt
from load_model import load_causal_lm
from lofi_ops import top_k_indices
from matrix_common import write_json

_PROXY = {
    "self_lp": proxy_fitness_gene,
    "ce": proxy_ce_fitness_gene,
}


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_deck(
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
    top_k: int = 2,
    eval_max_new: int | None = None,
    proxy: str = "self_lp",
    hypothesis: str = "H-DECK",
) -> dict[str, Any]:
    if proxy not in _PROXY:
        raise ValueError(f"run_h_deck: unknown proxy {proxy!r}")
    proxy_fn = _PROXY[proxy]
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    tok = teacher.tokenizer
    device = teacher.device
    student = load_student_ckpt(student_ckpt, tok, device)
    prompts = _prompts(prompts_path)
    pop = [random_gene(rng) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_fit = float("-inf")
    teacher_forwards = 0
    t0 = time.perf_counter()
    for gen in range(generations):
        proxies = [
            proxy_fn(
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
        fits = [float("-inf")] * pop_size
        for i in top:
            fits[i] = fitness_gene(
                pop[i],
                teacher=teacher,
                student=student,
                prompts=prompts,
                max_new=max_new,
                seed=seed + 2000 * gen + i,
            )
            teacher_forwards += len(prompts)
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        history.append({"gen": gen, "best_fit": fits[ranked[0]], "top_k": top})
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_gene = clamp_gene(pop[ranked[0]])
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)] if fits[i] > float("-inf")]
        if not parents:
            parents = [pop[i] for i in top]
        pop = [
            mutate_gene(parents[i % len(parents)], rng) for i in range(pop_size)
        ]
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    eval_fit = fitness_gene(
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
        "hypothesis": hypothesis,
        "proxy": proxy,
        "top_k": top_k,
        "best_gene": best_gene,
        "best_fit": best_fit,
        "eval_fit": eval_fit,
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
