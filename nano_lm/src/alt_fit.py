"""Score H-ALT genes: teacher lp + wall + layer-scaled GFLOPs."""

from __future__ import annotations

from typing import Mapping

from alt_ops import AltGene, clamp_alt_gene
from decode_alt import decode_alt
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from lay_fit import tip_row
from lay_ops import scale_flops_by_layers
from layer_exit import n_transformer_layers
from load_model import LoadedModel
from short_fit import fitness_early_detail
from student_model import count_params

__all__ = ["fitness_alt_detail", "fitness_early_detail", "tip_row"]


def fitness_alt_detail(
    alt: AltGene,
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, float]:
    """
    GIVEN alt-depth + frozen EARLY tip genes
    WHEN decoding
    THEN return (mean teacher_lp, mean wall_ms, mean est_gflops).
    """
    e = clamp_early_gene(early)
    g = clamp_alt_gene(alt, e)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    n_layers = n_transformer_layers(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_alt(
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
            alt_period=int(g["alt_period"]),
            shallow_skip=int(g["shallow_skip"]),
            start_shallow=bool(g["start_shallow"]),
            seed=seed + i,
            device=device,
        )
        walls.append(result.wall_ms)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        full = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        scaled = scale_flops_by_layers(
            full,
            layer_evals=int(result.layer_evals or 0),
            token_evals=int(result.token_evals),
            n_layers=n_layers,
        )
        gflops.append(to_gflops(scaled))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n
