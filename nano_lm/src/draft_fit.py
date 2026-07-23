"""Score speculative draft genes (student draft + teacher verify)."""

from __future__ import annotations

import time

from decode_spec import decode_spec
from draft_ops import DraftGene, clamp_draft_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_draft_detail(
    gene: DraftGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN a draft gene and prompts
    WHEN running decode_spec
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_draft_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
        result = decode_spec(
            student,
            teacher.model,
            tok,
            text,
            draft_len=int(g["draft_len"]),
            max_new_tokens=max_new,
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            seed=seed + i,
            device=device,
        )
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
