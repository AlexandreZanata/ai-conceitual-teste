"""Score H-REP genes: teacher lp + wall + est GFLOPs."""

from __future__ import annotations

from typing import Any, Mapping

from decode_rep import decode_rep
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from rep_ops import RepGene, clamp_rep_gene
from short_fit import fitness_early_detail, tip_row
from student_model import count_params

__all__ = ["fitness_rep_detail", "fitness_early_detail", "tip_row"]


def fitness_rep_detail(
    rep: RepGene,
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, float]:
    """
    GIVEN rep gene + frozen EARLY tip
    WHEN decoding
    THEN return (mean teacher_lp, mean wall_ms, mean est_gflops).
    """
    e = clamp_early_gene(early)
    g = clamp_rep_gene(rep, e)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_rep(
            student,
            tok,
            text,
            n=int(e["n"]),
            max_new_tokens=max_new,
            min_new=int(e["min_new"]),
            conf_threshold=float(e["conf_threshold"]),
            patience=int(e["patience"]),
            temperature=float(e["temperature"]),
            top_p=float(e["top_p"]),
            rep_penalty=float(g["rep_penalty"]),
            no_repeat_ngram=int(g["no_repeat_ngram"]),
            seed=seed + i,
            device=device,
        )
        walls.append(result.wall_ms)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        flops = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(flops))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n
