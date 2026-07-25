"""Score H-FUSEB: dual-budget FLASH ⊕ gated KV under CHBAT batch path."""

from __future__ import annotations

from typing import Any

from bat_score import score_batch_early, tip_row
from cbat_score import score_batch_cbat
from early_ops import EarlyGene
from flash_ops import gpt_neo_sdpa_context
from fuseb_ops import FUSEB_CHUNK
from kvsel_ops import SMOKE_BUDGETS, should_use_kv

__all__ = [
    "score_batch_chbat_dual",
    "score_batch_fuseb",
    "tip_row",
    "FUSEB_CHUNK",
    "SMOKE_BUDGETS",
]


def _mean_metrics(rows: list[dict[str, float]]) -> dict[str, float]:
    n = max(len(rows), 1)
    keys = ("mean_lp", "mean_wall_ms", "mean_tps", "mean_gflops", "n_new_total", "wall_sum_ms")
    out = {k: sum(float(r[k]) for r in rows) / n for k in keys}
    return out


def score_batch_chbat_dual(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    seed: int,
    chunk_size: int = FUSEB_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """Always-on CHBAT (chunked KV) under SDPA across dual budgets."""
    rows: list[dict[str, float]] = []
    with gpt_neo_sdpa_context():
        for b in budgets:
            m = score_batch_cbat(
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


def score_batch_fuseb(
    *,
    teacher: Any,
    student: object,
    prompts: list[str],
    gene: EarlyGene,
    seed: int,
    kv_threshold: int,
    chunk_size: int = FUSEB_CHUNK,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> dict[str, float]:
    """
    GIVEN EARLY tip + KVSEL threshold + CHBAT chunk under SDPA
    WHEN decoding dual budgets (chunked CBAT iff gated KV on; else flat BAT)
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
                m = score_batch_early(
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
