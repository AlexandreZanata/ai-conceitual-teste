"""Score DECM best_gene × ngram_size with teacher_lp + wall."""

from __future__ import annotations

from typing import Any

from decode_bon_ngram import decode_bon_ngram
from decode_genes import clamp_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_ngdm_detail(
    decm_gene: dict[str, Any],
    ngram_size: int,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN DECM gene knobs + ngram_size
    WHEN BoN+ngram decode (ignore use_mae; use n/T/top_p)
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_gene(decm_gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_bon_ngram(
            student,
            tok,
            text,
            n=int(g["n"]),
            max_new_tokens=max_new,
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
