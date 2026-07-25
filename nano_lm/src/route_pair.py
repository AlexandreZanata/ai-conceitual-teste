"""Shared H-GALL / H-GRAPHF / H-ROUTE seed trio."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from eval_decode import load_pair
from lay_ops import clamp_lay_gene
from poolb_score import throughput_gene
from route_ops import ROUTE_CHUNK
from route_score import SMOKE_BUDGETS, score_route_trio, tip_row

__all__ = ["run_seed_pair", "ROUTE_CHUNK", "SMOKE_BUDGETS"]


def _load_gene(path: Path) -> dict[str, Any]:
    if not path.is_file():
        raise FileNotFoundError(f"missing gene file: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return gene


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    return {
        **_load_gene(early_dir / f"HEARLY_seed{seed}_train.json"),
        "n": 1,
        "temperature": 1e-6,
    }


def _pool_gene(pool_dir: Path, seed: int) -> dict[str, Any]:
    eval_p = pool_dir / f"HPOOL_seed{seed}_eval.json"
    train_p = pool_dir / f"HPOOL_seed{seed}_train.json"
    path = eval_p if eval_p.is_file() else train_p
    return throughput_gene(_load_gene(path))


def _lay_gene(lay_dir: Path, seed: int) -> dict[str, Any]:
    gene = _load_gene(lay_dir / f"HLAY_seed{seed}_eval.json")
    if "max_skip" not in gene or "lay_conf" not in gene:
        raise ValueError(f"LAY missing max_skip/lay_conf: {lay_dir}")
    return clamp_lay_gene(gene)


def _kv_threshold(kvsel_dir: Path, seed: int) -> int:
    gene = _load_gene(kvsel_dir / f"HKVSEL_seed{seed}_eval.json")
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {kvsel_dir}")
    return int(gene["kv_threshold"])


def run_seed_pair(
    c: dict[str, Any],
    seed: int,
    prompts: list[str],
    *,
    claim_offset: int = 9191,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> list[dict[str, Any]]:
    """
    GIVEN shared B2 + tip genes
    WHEN scoring GALL, GRAPHF, and ROUTE (short→GALL, long→GRAPHF)
    THEN return tip_row for all three families.
    """
    gene_dir = Path(c.get("gene_dir", c["out"]))
    early_dir = Path(c.get("early_dir", gene_dir))
    pool_dir = Path(c.get("pool_dir", gene_dir))
    lay_dir = Path(c.get("lay_dir", gene_dir))
    kvsel_dir = Path(c.get("kvsel_dir", gene_dir))
    ckpt_dir = Path(c.get("ckpt_dir", gene_dir))
    early = _early_gene(early_dir, seed)
    pool = _pool_gene(pool_dir, seed)
    lay = _lay_gene(lay_dir, seed)
    thr = _kv_threshold(kvsel_dir, seed)
    ckpt = ckpt_dir / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + claim_offset
    trio = score_route_trio(
        teacher=teacher,
        student=student,
        prompts=prompts,
        early_gene=early,
        pool_gene=pool,
        lay=lay,
        kv_threshold=thr,
        seed=claim,
        chunk_size=ROUTE_CHUNK,
        budgets=budgets,
    )
    rows: list[dict[str, Any]] = []
    meta = {
        "kv_threshold": thr,
        "chunk_size": ROUTE_CHUNK,
        "budgets": list(budgets),
    }
    rows.append(
        tip_row(
            "H-GALL",
            f"HGALL_route_seed{seed}",
            trio["H-GALL"],
            seed,
            {**early, **lay, **meta, "backend": "sdpa+lay+cudagraph-all"},
        )
    )
    rows.append(
        tip_row(
            "H-GRAPHF",
            f"HGRAPHF_route_seed{seed}",
            trio["H-GRAPHF"],
            seed,
            {**pool, **lay, **meta, "backend": "sdpa+pool+lay+graphf-dual"},
        )
    )
    rows.append(
        tip_row(
            "H-ROUTE",
            f"HROUTE_seed{seed}",
            trio["H-ROUTE"],
            seed,
            {
                **lay,
                **meta,
                "backend": "short=GALL; long=GRAPHF/KV",
            },
        )
    )
    return rows
