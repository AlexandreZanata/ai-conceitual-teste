"""Score H-EARS genes with teacher log-prob + wall."""

from __future__ import annotations

import time

from decode_ears import decode_ears
from ears_ops import EarsGene, clamp_ears_gene
from eval_student import teacher_mean_logprob
from load_model import LoadedModel


def fitness_ears_detail(
    gene: EarsGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN an ears gene and prompts
    WHEN decoding with scheduled early-exit thr
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_ears_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        t0 = time.perf_counter()
        result = decode_ears(
            student,
            tok,
            text,
            n=int(g["n"]),
            max_new_tokens=max_new,
            min_new=int(g["min_new"]),
            conf_threshold=float(g["conf_threshold"]),
            patience=int(g["patience"]),
            len_coef=float(g["len_coef"]),
            budget_coef=float(g["budget_coef"]),
            prompt_ref=int(g["prompt_ref"]),
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            seed=seed + i,
            device=device,
        )
        walls.append((time.perf_counter() - t0) * 1000.0)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
