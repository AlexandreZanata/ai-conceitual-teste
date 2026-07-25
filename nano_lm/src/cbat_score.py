"""Score H-CBAT: chunked KV prefill under batched EARLY (+ FLASH SDPA)."""

from __future__ import annotations

from bat_score import tip_row
from chunk_ops import DEFAULT_CHUNK
from decode_cbat import decode_early_batch_chunked
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flash_ops import gpt_neo_sdpa_context
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from load_model import LoadedModel
from student_model import count_params

__all__ = ["score_batch_cbat", "tip_row", "DEFAULT_CHUNK"]


def _gene(gene: EarlyGene) -> EarlyGene:
    e = clamp_early_gene(gene)
    if "n" in gene:
        e["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        e["temperature"] = float(gene["temperature"])
    return e


def score_batch_cbat(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    max_new: int,
    seed: int,
    chunk_size: int = DEFAULT_CHUNK,
) -> dict[str, float]:
    """
    GIVEN frozen EARLY throughput gene + chunk_size under SDPA
    WHEN decoding the prompt pack with chunked KV prefill
    THEN return mean_lp / tok/s / wall / gflops metrics.
    """
    e = _gene(gene)
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    with gpt_neo_sdpa_context():
        results, wall_ms = decode_early_batch_chunked(
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
            chunk_size=int(chunk_size),
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
    }
