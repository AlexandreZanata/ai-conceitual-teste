"""H-DECM search helpers: elite mixture + multi-gene claim."""

from __future__ import annotations

import time
from typing import Any

from dec_fit_ops import decode_with_gene, fitness_gene_detail
from decode_genes import Gene, clamp_gene
from decm_ops import MIX_M, best_index
from eval_student import teacher_mean_logprob
from load_model import LoadedModel
from lat2_ops import clamp_gene_lat2


def gene_key(g: Gene) -> tuple:
    c = clamp_gene(g)
    return (
        round(float(c["temperature"]), 3),
        round(float(c["top_p"]), 3),
        int(c["n"]),
        int(c["k"]),
        int(c["block"]),
        int(c["horizon"]),
        bool(c["use_mae"]),
    )


def elite_mixture(
    pop: list[Gene], scores: list[float], *, m: int = MIX_M
) -> list[Gene]:
    """
    GIVEN scored population
    WHEN taking elite mixture
    THEN return up to m unique genes by descending score (LAT2-clamped).
    """
    if m < 1:
        raise ValueError("elite_mixture: m must be >= 1")
    ranked = sorted(range(len(pop)), key=lambda i: scores[i], reverse=True)
    out: list[Gene] = []
    seen: set[tuple] = set()
    for i in ranked:
        g = clamp_gene_lat2(pop[i])
        k = gene_key(g)
        if k in seen:
            continue
        seen.add(k)
        out.append(g)
        if len(out) >= m:
            break
    if not out:
        raise ValueError("elite_mixture: empty result")
    return out


def claim_mixture(
    mixture: list[Gene],
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, list[int]]:
    """Decode each gene per prompt; pick by student self-lp; teacher-score."""
    if not mixture:
        raise ValueError("claim_mixture: empty mixture")
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    picks: list[int] = []
    for i, text in enumerate(prompts):
        proxies: list[float] = []
        results: list[Any] = []
        t0 = time.perf_counter()
        for j, g in enumerate(mixture):
            result = decode_with_gene(
                g, student, tok, text, max_new, seed + 100 * i + j, device
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
