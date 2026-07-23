"""H-STACK search: elite early-gene mixture + proxy claim."""

from __future__ import annotations

import time
from typing import Any

from decm_ops import best_index
from decode_early import decode_early
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel
from stack_ops import MIX_M, early_gene_key


def elite_early_mixture(
    pop: list[EarlyGene], scores: list[float], *, m: int = MIX_M
) -> list[EarlyGene]:
    """
    GIVEN scored early-exit population
    WHEN taking elite mixture
    THEN return up to m unique genes by descending score.
    """
    if m < 1:
        raise ValueError("elite_early_mixture: m must be >= 1")
    ranked = sorted(range(len(pop)), key=lambda i: scores[i], reverse=True)
    out: list[EarlyGene] = []
    seen: set[tuple] = set()
    for i in ranked:
        g = clamp_early_gene(pop[i])
        k = early_gene_key(g)
        if k in seen:
            continue
        seen.add(k)
        out.append(g)
        if len(out) >= m:
            break
    if not out:
        raise ValueError("elite_early_mixture: empty result")
    return out


def claim_early_mixture(
    mixture: list[EarlyGene],
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, list[int]]:
    """Decode each early gene per prompt; pick by student self-lp; teacher-score."""
    if not mixture:
        raise ValueError("claim_early_mixture: empty mixture")
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    picks: list[int] = []
    for i, text in enumerate(prompts):
        proxies: list[float] = []
        results: list[Any] = []
        t0 = time.perf_counter()
        for j, gene in enumerate(mixture):
            g = clamp_early_gene(gene)
            result = decode_early(
                student,
                tok,
                text,
                n=int(g["n"]),
                max_new_tokens=max_new,
                min_new=int(g["min_new"]),
                conf_threshold=float(g["conf_threshold"]),
                patience=int(g["patience"]),
                temperature=float(g["temperature"]),
                top_p=float(g["top_p"]),
                seed=seed + 100 * i + j,
                device=device,
            )
            results.append(result)
            proxies.append(float(result.mean_logprob))
        pi = best_index(proxies)
        picks.append(pi)
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(
            teacher_mean_logprob(teacher, ids, list(results[pi].token_ids))
        )
    return sum(scores) / len(scores), sum(walls) / len(walls), picks
