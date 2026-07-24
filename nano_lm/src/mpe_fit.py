"""Score H-MPE genes with teacher log-prob + wall."""

from __future__ import annotations

from decode_minp import decode_minp
from eval_student import teacher_mean_logprob
from load_model import LoadedModel
from mpe_ops import MpeGene, clamp_mpe_gene


def fitness_mpe_detail(
    gene: MpeGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN a min-p gene and prompts
    WHEN decoding with min-p filter
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_mpe_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_minp(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            min_p=float(g["min_p"]),
            seed=seed + i,
            device=device,
        )
        walls.append(float(result.wall_ms))
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
