"""Score H-TPE genes with teacher log-prob + wall."""

from __future__ import annotations

from decode_typ import decode_typ
from eval_student import teacher_mean_logprob
from load_model import LoadedModel
from tpe_ops import TpeGene, clamp_tpe_gene


def fitness_tpe_detail(
    gene: TpeGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float]:
    """
    GIVEN a typical gene and prompts
    WHEN decoding with typical filter
    THEN return (mean teacher_lp, mean wall_ms).
    """
    g = clamp_tpe_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    scores: list[float] = []
    walls: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_typ(
            student,
            tok,
            text,
            max_new_tokens=max_new,
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
            typ_mass=float(g["typ_mass"]),
            seed=seed + i,
            device=device,
        )
        walls.append(float(result.wall_ms))
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
    return sum(scores) / len(scores), sum(walls) / len(walls)
