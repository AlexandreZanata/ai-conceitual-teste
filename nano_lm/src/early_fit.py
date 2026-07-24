"""Score early-exit genes with teacher log-prob + wall."""

from __future__ import annotations

import time

from decode_early import decode_early
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_early_detail(
    gene: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
    student_device=None,
) -> tuple[float, float]:
    """
    GIVEN an early-exit gene and prompts
    WHEN decoding with confidence stop
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_early_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device if student_device is None else student_device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
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
            seed=seed + i,
            device=device,
        )
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
