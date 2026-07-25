"""Score H-QPACK: serial POOL tip + FLAYB pack on shared budgets."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from flayb_score import score_batch_flayb
from kvsel_ops import SMOKE_BUDGETS
from lay_ops import LayGene
from poolb_score import score_serial_pool
from qpack_ops import QPACK_CHUNK

__all__ = [
    "score_qpack_pair",
    "score_pool_budgets",
    "tip_row",
    "QPACK_CHUNK",
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


def score_pool_budgets(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: Mapping[str, Any],
    seed: int,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN POOL tip gene alone (serial decode)
    WHEN scoring across the same budgets as FLAYB
    THEN return mean lp / tok/s / wall / gflops.
    """
    rows: list[dict[str, float]] = []
    for b in budgets:
        claim = seed + 1000 * b
        rows.append(
            score_serial_pool(
                teacher=teacher,
                student=student,
                prompts=prompts,
                gene=gene,
                max_new=b,
                seed=claim,
            )
        )
    out = _mean_metrics(rows)
    out["n_prompts"] = float(len(prompts))
    return out


def score_qpack_pair(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    pool_gene: Mapping[str, Any],
    lay: LayGene | Mapping[str, float | int],
    kv_threshold: int,
    seed: int,
    chunk_size: int = QPACK_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[dict[str, float], dict[str, float]]:
    """
    GIVEN tip genes
    WHEN scoring serial POOL and FLAYB
    THEN return (pool, flayb).
    """
    pool = score_pool_budgets(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=pool_gene,
        seed=seed,
        budgets=budgets,
    )
    flayb = score_batch_flayb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=pool_gene,
        lay=lay,
        seed=seed,
        kv_threshold=kv_threshold,
        chunk_size=int(chunk_size),
        budgets=budgets,
    )
    return pool, flayb
