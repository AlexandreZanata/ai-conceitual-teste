"""Score H-NGE genes with teacher log-prob + wall."""

from __future__ import annotations

from decode_ngram import decode_ngram
from eval_student import teacher_mean_logprob
from load_model import LoadedModel
from nge_ops import NgeGene, clamp_nge_gene


def fitness_nge_detail(
    gene: NgeGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN an ngram gene and prompts
    WHEN decoding with no-repeat ban
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_nge_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_ngram(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            ngram_size=int(g["ngram_size"]),
            seed=seed + i,
            device=device,
        )
        walls.append(float(result.wall_ms))
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
