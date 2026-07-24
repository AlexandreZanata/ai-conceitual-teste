"""Score POOL/DECKL genes with teacher_lp + wall + est. GFLOPs."""

from __future__ import annotations

from collections.abc import Callable

from dec_fit_ops import decode_with_gene
from decode_genes import Gene, clamp_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from student_model import count_params


def fitness_poolf_detail(
    gene: Gene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
    clamp_fn: Callable[[Gene], Gene] = clamp_gene,
) -> tuple[float, float, float]:
    """
    GIVEN a decode gene and prompts
    WHEN scoring with teacher + FLOP estimate
    THEN return (mean teacher_lp, mean wall_ms, mean est_gflops).
    """
    g = clamp_fn(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_with_gene(g, student, tok, text, max_new, seed + i, device)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        walls.append(result.wall_ms)
        fl = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(fl))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n
