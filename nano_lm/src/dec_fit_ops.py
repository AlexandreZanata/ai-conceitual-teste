"""Shared decode-gene fitness: teacher score, timed score, student proxy."""

from __future__ import annotations

import time
from typing import Any

import torch

from decode_bon import decode_bon
from decode_genes import Gene, clamp_gene
from decode_mae import decode_mae
from eval_student import teacher_mean_logprob
from load_model import LoadedModel
from train_ce import ce_loss


def decode_with_gene(
    g: Gene, student: Any, tok: Any, text: str, max_new: int, seed: int, device: Any
) -> Any:
    gene = clamp_gene(g)
    if gene["use_mae"]:
        return decode_mae(
            student,
            tok,
            text,
            k=gene["k"],
            block=gene["block"],
            horizon=gene["horizon"],
            max_new_tokens=max_new,
            temperature=gene["temperature"],
            top_p=gene["top_p"],
            seed=seed,
            device=device,
        )
    return decode_bon(
        student,
        tok,
        text,
        n=gene["n"],
        max_new_tokens=max_new,
        temperature=gene["temperature"],
        top_p=gene["top_p"],
        seed=seed,
        device=device,
    )


def fitness_gene_detail(
    gene: Gene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN a decode gene and prompts
    WHEN scoring with teacher
    THEN return (mean teacher log-prob, mean wall_ms per prompt).
    """
    g = clamp_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
        result = decode_with_gene(g, student, tok, text, max_new, seed + i, device)
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)


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
    lp, _wall = fitness_gene_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed,
    )
    return lp


def proxy_fitness_gene(
    gene: Gene,
    *,
    student: object,
    tok: Any,
    device: Any,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> float:
    """
    GIVEN gene + prompts
    WHEN scoring without teacher
    THEN return mean student self log-prob of completions (cheap proxy).
    """
    g = clamp_gene(gene)
    scores: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_with_gene(g, student, tok, text, max_new, seed + i, device)
        scores.append(float(result.mean_logprob))
    return sum(scores) / len(scores)


def proxy_ce_fitness_gene(
    gene: Gene,
    *,
    student: object,
    tok: Any,
    device: Any,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> float:
    """
    GIVEN gene + prompts
    WHEN scoring without teacher
    THEN return mean −CE of student on prompt+completion (teacher-forced).
    """
    g = clamp_gene(gene)
    scores: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_with_gene(g, student, tok, text, max_new, seed + i, device)
        prompt_ids = tok.encode(text, return_tensors="pt").to(device)
        if not result.token_ids:
            scores.append(float("-inf"))
            continue
        comp = torch.tensor([list(result.token_ids)], device=device, dtype=torch.long)
        full = torch.cat([prompt_ids, comp], dim=1)
        with torch.no_grad():
            scores.append(-float(ce_loss(student(full).logits, full).item()))
    return sum(scores) / len(scores)
