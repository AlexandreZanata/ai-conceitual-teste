"""Score H-EAR2 genes with teacher log-prob + wall."""

from __future__ import annotations

import time

from decode_ear2 import decode_ear2
from ear2_ops import Ear2Gene, clamp_ear2_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_ear2_detail(
    gene: Ear2Gene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new_ceiling: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN an ear2 gene and prompts
    WHEN decoding with widened early-exit
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_ear2_gene(gene)
    hold = min(int(g["max_new"]), int(max_new_ceiling))
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
        result = decode_ear2(
            student,
            tok,
            text,
            n=int(g["n"]),
            max_new_tokens=hold,
            min_new=int(g["min_new"]),
            conf_threshold=float(g["conf_threshold"]),
            patience=int(g["patience"]),
            conf_metric=str(g["conf_metric"]),
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            seed=seed + i,
            device=device,
        )
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
