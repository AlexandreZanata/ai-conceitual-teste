"""Score H-BUD genes: EARLY decode with gene max_new budget."""

from __future__ import annotations

import time

from bud_ops import BudGene, clamp_bud_gene
from decode_early import decode_early
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_bud_detail(
    gene: BudGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new_ceiling: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN a bud gene and prompts
    WHEN decoding with early-exit under gene max_new
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_bud_gene(gene)
    hold = min(int(g["max_new"]), int(max_new_ceiling))
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
        result = decode_early(
            student,
            tok,
            text,
            n=int(g["n"]),
            max_new_tokens=hold,
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
