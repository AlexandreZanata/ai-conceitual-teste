"""H-DECP helpers: evolve one gene; claim via proxy-picked bank genes."""

from __future__ import annotations

import random
import time

from dec_fit_ops import decode_with_gene, fitness_gene, proxy_fitness_gene
from decode_genes import Gene, clamp_gene, mutate_gene, random_gene
from decp_ops import best_index
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def evolve_gene(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    pop_size: int,
    generations: int,
    max_new: int,
    seed: int,
) -> tuple[Gene, float]:
    """Evolve one decode gene on prompts; return (best_gene, best_fit)."""
    rng = random.Random(seed)
    pop = [random_gene(rng) for _ in range(pop_size)]
    best_gene, best_fit = pop[0], float("-inf")
    for gen in range(generations):
        fits = [
            fitness_gene(
                g,
                teacher=teacher,
                student=student,
                prompts=prompts,
                max_new=max_new,
                seed=seed + 1000 * gen,
            )
            for g in pop
        ]
        ranked = sorted(range(pop_size), key=lambda i: fits[i], reverse=True)
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_gene = clamp_gene(pop[ranked[0]])
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
        pop = [mutate_gene(parents[i % len(parents)], rng) for i in range(pop_size)]
    return best_gene, best_fit


def claim_with_bank(
    bank: list[Gene],
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, list[int]]:
    """
    For each prompt, pick bank gene by student proxy; teacher-score claim.
    Returns (mean_lp, mean_wall_ms, picked_indices).
    """
    if not bank:
        raise ValueError("claim_with_bank: empty bank")
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    picks: list[int] = []
    for i, text in enumerate(prompts):
        proxies = [
            proxy_fitness_gene(
                g,
                student=student,
                tok=tok,
                device=device,
                prompts=[text],
                max_new=max_new,
                seed=seed + 100 * i + j,
            )
            for j, g in enumerate(bank)
        ]
        pi = best_index(proxies)
        picks.append(pi)
        t0 = time.perf_counter()
        result = decode_with_gene(
            bank[pi], student, tok, text, max_new, seed + 777 + i, device
        )
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls), picks
