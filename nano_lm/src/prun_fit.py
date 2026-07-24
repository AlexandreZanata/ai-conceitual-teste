"""Score STAG/H-PRUN students with frozen EARLY genes + density-scaled FLOPs."""

from __future__ import annotations

from typing import Any

from decode_early import decode_early
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from prun_mask import density_of
from prun_ops import scale_flops_by_density
from student_model import count_params


def score_early_flops(
    gene: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
    density: float | None = None,
) -> tuple[float, float, float]:
    """
    GIVEN EARLY tip genes and a student
    WHEN decoding
    THEN return (mean lp, mean wall_ms, mean est_gflops).
    """
    g = clamp_early_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    dens = float(density) if density is not None else density_of(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_early(
            student,
            tok,
            text,
            n=int(g["n"]),
            max_new_tokens=max_new,
            min_new=int(g["min_new"]),
            conf_threshold=float(g["conf_threshold"]),
            patience=int(g["patience"]),
            temperature=float(g["temperature"]),
            top_p=float(g["top_p"]),
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
        gflops.append(to_gflops(scale_flops_by_density(full, density=dens)))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n


def row(
    family: str,
    label: str,
    lp: float,
    wall: float,
    gf: float,
    seed: int,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    out: dict[str, Any] = {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "mean_est_gflops": float(gf),
        "n_prompts": 2,
        "seed": seed,
    }
    if extra:
        out.update(extra)
    return out
