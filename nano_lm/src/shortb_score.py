"""Score H-SHORTB: dual-budget FUSEB path with SHORT on non-KV arm."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from cbat_score import score_batch_cbat
from decode_short_batch import decode_short_batch
from early_ops import EarlyGene, clamp_early_gene
from eval_student import teacher_mean_logprob
from flash_ops import gpt_neo_sdpa_context
from flop_ops import est_decode_flops, to_gflops, tokens_per_s
from fuseb_score import score_batch_fuseb
from kvsel_ops import SMOKE_BUDGETS, should_use_kv
from load_model import LoadedModel
from short_ops import ShortGene, clamp_short_gene
from shortb_ops import SHORTB_CHUNK
from student_model import count_params

__all__ = [
    "score_batch_short",
    "score_batch_shortb",
    "score_batch_fuseb",
    "tip_row",
    "SHORTB_CHUNK",
    "SMOKE_BUDGETS",
]


def _gene(gene: EarlyGene) -> EarlyGene:
    e = clamp_early_gene(gene)
    if "n" in gene:
        e["n"] = int(max(1, int(gene["n"])))
    if "temperature" in gene:
        e["temperature"] = float(gene["temperature"])
    return e


def _mean_metrics(rows: list[dict[str, float]]) -> dict[str, float]:
    n = max(len(rows), 1)
    keys = (
        "mean_lp",
        "mean_wall_ms",
        "mean_tps",
        "mean_gflops",
        "n_new_total",
        "wall_sum_ms",
    )
    return {k: sum(float(r[k]) for r in rows) / n for k in keys}


def score_batch_short(
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    short: ShortGene | Mapping[str, Any],
    max_new: int,
    seed: int,
) -> dict[str, float]:
    """Batched SHORT decode under caller SDPA."""
    e = _gene(gene)
    g = clamp_short_gene(short, e)
    draft_max = min(int(g["draft_max"]), int(max_new))
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    results, wall_ms = decode_short_batch(
        student,
        tok,
        prompts,
        n=int(e["n"]),
        max_new_tokens=max_new,
        draft_max=draft_max,
        stop_conf=float(g["stop_conf"]),
        min_new=int(e["min_new"]),
        conf_threshold=float(e["conf_threshold"]),
        patience=int(e["patience"]),
        temperature=float(e["temperature"]),
        top_p=float(e["top_p"]),
        seed=seed,
        device=device,
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


def score_batch_shortb(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    short: ShortGene | Mapping[str, Any],
    seed: int,
    kv_threshold: int,
    chunk_size: int = SHORTB_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN EARLY tip + SHORT tip + KVSEL threshold under SDPA
    WHEN dual budgets (CHBAT iff KV on; else batched SHORT)
    THEN return mean lp / tok/s / wall / gflops.
    """
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            claim = seed + 1000 * b
            if should_use_kv(b, kv_threshold):
                m = score_batch_cbat(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=gene,
                    max_new=b,
                    seed=claim,
                    chunk_size=int(chunk_size),
                )
            else:
                m = score_batch_short(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=gene,
                    short=short,
                    max_new=b,
                    seed=claim,
                )
            rows.append(m)
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out
