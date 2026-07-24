"""Score length-bucketed EARLY decode (throughput + teacher lp)."""

from __future__ import annotations

from typing import Any

from bucket_ops import DEFAULT_BAND
from decode_bucket import decode_early_bucketed
from early_ops import clamp_early_gene
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from load_model import LoadedModel
from student_model import count_params


def _gene(gene: dict[str, Any]) -> dict[str, Any]:
    e = clamp_early_gene(gene)
    if "n" in gene:
        e["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        e["temperature"] = float(gene["temperature"])
    return e


def score_bucket_early(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: dict[str, Any],
    max_new: int,
    seed: int,
    band: int = DEFAULT_BAND,
) -> dict[str, float]:
    e = _gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    results, wall_ms, n_buckets = decode_early_bucketed(
        student,
        tok,
        prompts,
        n=int(e["n"]),
        max_new_tokens=max_new,
        min_new=int(e["min_new"]),
        conf_threshold=float(e["conf_threshold"]),
        patience=int(e["patience"]),
        temperature=float(e["temperature"]),
        top_p=float(e["top_p"]),
        seed=seed,
        device=device,
        band=band,
    )
    lps: list[float] = []
    gflops: list[float] = []
    n_new_total = 0
    for text, result in zip(prompts, results):
        n_new_total += len(result.token_ids)
        ids = tok.encode(text, return_tensors="pt")
        lps.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        flops = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        gflops.append(to_gflops(flops))
    n = max(len(lps), 1)
    return {
        "mean_lp": sum(lps) / n,
        "mean_wall_ms": float(wall_ms) / n,
        "mean_tps": tokens_per_s(n_new=n_new_total, wall_ms=wall_ms),
        "mean_gflops": sum(gflops) / n,
        "n_new_total": float(n_new_total),
        "wall_sum_ms": float(wall_ms),
        "n_buckets": float(n_buckets),
    }
