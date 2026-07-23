"""H-DEC: evolve decode knobs; fitness = teacher score on fixed prompts."""

from __future__ import annotations

import random
import time
from pathlib import Path
from typing import Any

import yaml

from decode_bon import decode_bon
from decode_genes import Gene, clamp_gene, mutate_gene, random_gene
from decode_mae import decode_mae
from eval_student import load_student_ckpt, teacher_mean_logprob
from load_model import LoadedModel, load_causal_lm
from matrix_common import write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _decode_with_gene(
    g: Gene, student: Any, tok: Any, text: str, max_new: int, seed: int, device: Any
) -> Any:
    if g["use_mae"]:
        return decode_mae(
            student,
            tok,
            text,
            k=g["k"],
            block=g["block"],
            horizon=g["horizon"],
            max_new_tokens=max_new,
            temperature=g["temperature"],
            top_p=g["top_p"],
            seed=seed,
            device=device,
        )
    return decode_bon(
        student,
        tok,
        text,
        n=g["n"],
        max_new_tokens=max_new,
        temperature=g["temperature"],
        top_p=g["top_p"],
        seed=seed,
        device=device,
    )


def fitness_gene(
    gene: Gene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> float:
    """Mean teacher log-prob of completions under gene decode policy."""
    g = clamp_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    for i, text in enumerate(prompts):
        result = _decode_with_gene(
            g, student, tok, text, max_new, seed + i, device
        )
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores)


def run_h_dec(
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
    eval_max_new: int | None = None,
) -> dict[str, Any]:
    rng = random.Random(seed)
    teacher = load_causal_lm(
        teacher_id, tokenizer_id, cache_dir=cache_dir, use_fp16=True
    )
    student = load_student_ckpt(student_ckpt, teacher.tokenizer, teacher.device)
    prompts = _prompts(prompts_path)
    pop = [random_gene(rng) for _ in range(pop_size)]
    history: list[dict[str, Any]] = []
    best_gene = pop[0]
    best_fit = float("-inf")
    t0 = time.perf_counter()
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
        history.append(
            {
                "gen": gen,
                "best_fit": fits[ranked[0]],
                "genes": [dict(x) for x in pop],
            }
        )
        if fits[ranked[0]] > best_fit:
            best_fit = fits[ranked[0]]
            best_gene = clamp_gene(pop[ranked[0]])
        parents = [pop[i] for i in ranked[: max(1, pop_size // 2)]]
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
    meta = {
        "hypothesis": "H-DEC",
        "best_gene": best_gene,
        "best_fit": best_fit,
        "eval_fit": eval_fit,
        "eval_max_new": hold,
        "history": history,
        "wall_s": time.perf_counter() - t0,
        "student_ckpt": str(student_ckpt),
    }
    write_json(out_meta, meta)
    return meta
