"""Shared H-EARLY / H-SKIP / H-LAYB seed trio for H-BPACK."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from bpack_ops import BPACK_CHUNK
from bpack_score import SMOKE_BUDGETS, score_bpack_trio, tip_row
from eval_decode import load_pair
from lay_ops import clamp_lay_gene

__all__ = ["run_seed_trio", "BPACK_CHUNK", "SMOKE_BUDGETS"]


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


def run_seed_trio(
    c: dict[str, Any],
    seed: int,
    prompts: list[str],
    *,
    claim_offset: int = 9911,
    budgets: tuple[int, ...] = SMOKE_BUDGETS,
) -> list[dict[str, Any]]:
    """
    GIVEN shared B2 + tip genes
    WHEN scoring EARLY, SKIP, and LAYB packs
    THEN return tip_row for all three families.
    """
    gene_dir = Path(c.get("gene_dir", c["out"]))
    early_dir = Path(c.get("early_dir", gene_dir))
    lay_dir = Path(c.get("lay_dir", gene_dir))
    kvsel_dir = Path(c.get("kvsel_dir", gene_dir))
    ckpt_dir = Path(c.get("ckpt_dir", gene_dir))
    early = _early_gene(early_dir, seed)
    lay = _lay_gene(lay_dir, seed)
    thr = _kv_threshold(kvsel_dir, seed)
    ckpt = ckpt_dir / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + claim_offset
    early_m, skip, layb = score_bpack_trio(
        teacher=teacher,
        student=student,
        prompts=prompts,
        early_gene=early,
        lay=lay,
        kv_threshold=thr,
        seed=claim,
        chunk_size=BPACK_CHUNK,
        budgets=budgets,
    )
    meta = {
        "kv_threshold": thr,
        "chunk_size": BPACK_CHUNK,
        "budgets": list(budgets),
    }
    return [
        tip_row(
            "H-EARLY",
            f"HEARLY_bpack_seed{seed}",
            early_m,
            seed,
            {**early, **meta, "backend": "serial-early"},
        ),
        tip_row(
            "H-SKIP",
            f"HSKIP_bpack_seed{seed}",
            skip,
            seed,
            {**early, **meta, "backend": "sdpa+chunk+bat+chb; skip-cbat"},
        ),
        tip_row(
            "H-LAYB",
            f"HLAYB_bpack_seed{seed}",
            layb,
            seed,
            {**lay, **meta, "backend": "sdpa+lay+kvsel+chbat"},
        ),
    ]
