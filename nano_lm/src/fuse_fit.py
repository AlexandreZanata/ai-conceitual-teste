"""Score H-FUSE: FLASH SDPA ⊕ KVSEL gated KV on dual budgets."""

from __future__ import annotations

from early_ops import EarlyGene
from flash_fit import fitness_flash_detail
from flash_ops import gpt_neo_sdpa_context
from kvsel_fit import fitness_kvsel_detail
from kvsel_ops import SMOKE_BUDGETS
from load_model import LoadedModel
from short_fit import tip_row

__all__ = [
    "fitness_flash_dual",
    "fitness_fuse_detail",
    "tip_row",
]


def _mean3(rows: list[tuple[float, float, float]]) -> tuple[float, float, float]:
    n = max(len(rows), 1)
    return (
        sum(r[0] for r in rows) / n,
        sum(r[1] for r in rows) / n,
        sum(r[2] for r in rows) / n,
    )


def fitness_flash_dual(
    early: EarlyGene,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    seed: int,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[float, float, float]:
    """Mean (lp, wall, gflops) for FLASH across decode budgets."""
    rows = [
        fitness_flash_detail(
            early,
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=b,
            seed=seed + 1000 * b,
        )
        for b in budgets
    ]
    return _mean3(rows)


def fitness_fuse_detail(
    early: EarlyGene,
    kv_threshold: int,
    *,
    teacher: LoadedModel,
    student: object,
    prompts: list[str],
    seed: int,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> tuple[float, float, float]:
    """
    GIVEN EARLY tip + KVSEL threshold under SDPA
    WHEN decoding dual budgets with gated KV
    THEN return mean (teacher_lp, wall_ms, est_gflops).
    """
    with gpt_neo_sdpa_context():
        return fitness_kvsel_detail(
            early,
            kv_threshold,
            teacher=teacher,
            student=student,
            prompts=prompts,
            seed=seed,
            budgets=budgets,
        )
