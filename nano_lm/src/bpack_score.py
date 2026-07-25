"""Score H-BPACK: EARLY + SKIP + LAYB on shared budgets."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from cbat_score import score_batch_cbat
from early_ops import EarlyGene
from kvsel_ops import SMOKE_BUDGETS
from lay_ops import LayGene
from layb_score import score_batch_layb
from bpack_ops import BPACK_CHUNK, SKIP_CHUNK
from serve_score import score_early_budgets

__all__ = [
    "score_bpack_trio",
    "tip_row",
    "BPACK_CHUNK",
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


def score_skip_budgets(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    seed: int,
    chunk_size: int = SKIP_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """CHB-chunk batch (SKIP) mean across the same budgets as LAYB."""
    rows: list[dict[str, float]] = []
    for b in budgets:
        claim = seed + 1000 * b
        rows.append(
            score_batch_cbat(
                teacher=teacher,
                student=student,
                prompts=prompts,
                gene=gene,
                max_new=b,
                seed=claim,
                chunk_size=int(chunk_size),
            )
        )
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out


def score_bpack_trio(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    early_gene: EarlyGene,
    lay: LayGene | Mapping[str, float | int],
    kv_threshold: int,
    seed: int,
    chunk_size: int = BPACK_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[dict[str, float], dict[str, float], dict[str, float]]:
    """
    GIVEN tip genes
    WHEN scoring serial EARLY, SKIP, and LAYB
    THEN return (early, skip, layb).
    """
    early = score_early_budgets(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=early_gene,
        seed=seed,
        budgets=budgets,
    )
    skip = score_skip_budgets(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=early_gene,
        seed=seed,
        chunk_size=SKIP_CHUNK,
        budgets=budgets,
    )
    layb = score_batch_layb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=early_gene,
        lay=lay,
        seed=seed,
        kv_threshold=kv_threshold,
        chunk_size=int(chunk_size),
        budgets=budgets,
    )
    return early, skip, layb
