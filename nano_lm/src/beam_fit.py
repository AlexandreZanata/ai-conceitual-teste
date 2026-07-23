"""Score beam genes with teacher log-prob + wall."""

from __future__ import annotations

import time

from beam_ops import BeamGene, clamp_beam_gene
from decode_beam import decode_beam
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_beam_detail(
    gene: BeamGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN a beam gene and prompts
    WHEN decoding with beam search
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_beam_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
        result = decode_beam(
            student,
            tok,
            text,
            beam_width=int(g["beam_width"]),
            max_new_tokens=max_new,
            length_penalty=float(g["length_penalty"]),
            seed=seed + i,
            device=device,
        )
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
