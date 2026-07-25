"""Score H-FCPOOLB: dual-budget FLASH ⊕ gated KV under CPOOLB path."""

from __future__ import annotations

from typing import Any

from bat_score import tip_row
from cpoolb_score import score_batch_cpoolb
from decode_genes import Gene
from fcpoolb_ops import FCPOOLB_CHUNK
from flash_ops import gpt_neo_sdpa_context
from kvsel_ops import SMOKE_BUDGETS, should_use_kv
from poolb_score import score_batch_pool

__all__ = [
    "score_batch_cpoolb_dual",
    "score_batch_fcpoolb",
    "tip_row",
    "FCPOOLB_CHUNK",
    "SMOKE_BUDGETS",
]


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


def score_batch_cpoolb_dual(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: Gene,
    seed: int,
    chunk_size: int = FCPOOLB_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """Always-on CPOOLB (chunked KV) under SDPA across dual budgets."""
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            m = score_batch_cpoolb(
                teacher=teacher,
                student=student,
                prompts=prompts,
                gene=gene,
                max_new=b,
                seed=seed + 1000 * b,
                chunk_size=int(chunk_size),
            )
            rows.append(m)
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out


def score_batch_fcpoolb(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: Gene,
    seed: int,
    kv_threshold: int,
    chunk_size: int = FCPOOLB_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN POOL tip + KVSEL threshold + CPOOLB chunk under SDPA
    WHEN decoding dual budgets (chunked CPOOLB iff gated KV on; else flat POOLB)
    THEN return mean lp / tok/s / wall / gflops.
    """
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            claim = seed + 1000 * b
            if should_use_kv(b, kv_threshold):
                m = score_batch_cpoolb(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=gene,
                    max_new=b,
                    seed=claim,
                    chunk_size=int(chunk_size),
                )
            else:
                m = score_batch_pool(
                    teacher=teacher,
                    student=student,
                    prompts=prompts,
                    gene=gene,
                    max_new=b,
                    seed=claim,
                )
            rows.append(m)
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out
