"""Score H-PACK: EARLY tip + SERVE + SROUTE on shared budgets."""

from __future__ import annotations

from typing import Any, Mapping

from bat_score import tip_row
from early_ops import EarlyGene
from kvsel_ops import SMOKE_BUDGETS
from lay_ops import LayGene
from pack_ops import PACK_CHUNK
from route_score import score_batch_route
from serve_score import score_serve_candidates

__all__ = ["score_pack_trio", "tip_row", "PACK_CHUNK", "SMOKE_BUDGETS"]


def score_pack_trio(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    early_gene: EarlyGene,
    pool_gene: Mapping[str, Any],
    lay: LayGene | Mapping[str, float | int],
    kv_threshold: int,
    seed: int,
    chunk_size: int = PACK_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[str, dict[str, float], dict[str, float], dict[str, float]]:
    """
    GIVEN tip genes
    WHEN scoring serial EARLY, frozen SERVE pick, and ROUTE
    THEN return (recipe, early, serve, sroute).
    """
    recipe, serve, all_m = score_serve_candidates(
        teacher=teacher,
        student=student,
        prompts=prompts,
        early_gene=early_gene,
        pool_gene=pool_gene,
        lay=lay,
        kv_threshold=kv_threshold,
        seed=seed,
        chunk_size=int(chunk_size),
        budgets=budgets,
    )
    sroute = score_batch_route(
        teacher=teacher,
        student=student,
        prompts=prompts,
        early_gene=early_gene,
        pool_gene=pool_gene,
        lay=lay,
        seed=seed,
        kv_threshold=kv_threshold,
        chunk_size=int(chunk_size),
        budgets=budgets,
    )
    return recipe, all_m["early"], serve, sroute
