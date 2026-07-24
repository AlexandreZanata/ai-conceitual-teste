"""Score fp32 EARLY tip vs AMP autocast decode (same genes/ckpt)."""

from __future__ import annotations

from typing import Any, Mapping

from amp_ops import cast_student_amp, resolve_amp_dtype
from decode_early import decode_early
from decode_early_amp import decode_early_amp
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from load_model import LoadedModel
from student_model import count_params


def _row(
    family: str,
    label: str,
    lp: float,
    wall: float,
    gf: float,
    seed: int,
    extra: Mapping[str, Any] | None = None,
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
        out.update(dict(extra))
    return out


def score_early_fp32(
    gene: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
) -> tuple[float, float, float]:
    g = clamp_early_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
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
        fl = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(fl))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n


def score_early_amp(
    gene: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    max_new: int,
    seed: int,
    amp_kind: str,
) -> tuple[float, float, float, str]:
    g = clamp_early_gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    dtype = resolve_amp_dtype(amp_kind, device)
    cast_student_amp(student, dtype)
    n_params = count_params(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_early_amp(
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
            amp_dtype=dtype,
        )
        walls.append(result.wall_ms)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        fl = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(fl))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n, str(dtype)
