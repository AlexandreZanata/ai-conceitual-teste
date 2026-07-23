"""H-DECQ: quantized gene search → elite mixture claim (like H-DECM)."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from dec_fit_ops import fitness_gene_detail
from decm_ops import MIX_M
from decm_search import claim_mixture, elite_mixture
from decq_ops import mutate_gene_decq, quantize_gene, random_gene_decq
from eval_student import load_student_ckpt
from lat2_ops import MIN_LAM
from lat_ops import latency_aware_score
from load_model import load_causal_lm
from matrix_common import write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def run_h_decq(
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
    if lam < MIN_LAM:
        raise ValueError(f"run_h_decq: lam must be >= {MIN_LAM}")
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    fit_prompts = _prompts(prompts_path)
    claim_path = eval_prompts_path if eval_prompts_path is not None else prompts_path
    claim_prompts = _prompts(claim_path)
    hold = int(eval_max_new) if eval_max_new is not None else max_new
    pop = [random_gene_decq(rng) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for gen in range(generations):
        details = [
            fitness_gene_detail(
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
            mutate_gene_decq(parents[i % len(parents)], rng) for i in range(pop_size)
        ]
    details = [
        fitness_gene_detail(
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
    # elite_mixture clamps LAT2; re-quantize so codes stay discrete.
    mixture = [quantize_gene(g) for g in elite_mixture(pop, scores, m=mix_m)]
    mix_lp, mix_wall, picks = claim_mixture(
        mixture,
        teacher=teacher,
        student=student,
        prompts=claim_prompts,
        max_new=hold,
        seed=seed + 7777,
    )
    meta = {
        "hypothesis": "H-DECQ",
        "lam": lam,
        "mix_m": mix_m,
        "mixture": mixture,
        "best_gene": mixture[0],
        "best_fit": float(details[scores.index(max(scores))][0]),
        "eval_fit": mix_lp,
        "eval_wall_ms": mix_wall,
        "picks": picks,
        "eval_max_new": hold,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
