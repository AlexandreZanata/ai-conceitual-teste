"""Score NGRAM×EARLY stacked decode with teacher_lp + wall."""

from __future__ import annotations

from typing import Any

from decode_ngre import decode_ngre
from early_ops import clamp_early_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_ngre_detail(
    early_gene: dict[str, Any],
    ngram_size: int,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN early gene + ngram_size and prompts
    WHEN decoding with ban + early-exit
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_early_gene(early_gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_ngre(
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
            ngram_size=int(ngram_size),
            seed=seed + i,
            device=device,
        )
        walls.append(float(result.wall_ms))
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
