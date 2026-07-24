"""Smoke H-BUCKET: length-banded BAT vs flat H-BAT / serial EARLY."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from bat_score import score_batch_early, score_serial_early, tip_row
from bucket_ops import DEFAULT_BAND
from bucket_score import score_bucket_early
from eval_decode import load_pair
from load_model import resolve_device
from matrix_common import ROOT, matrix_cfg, write_json


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _load_texts(*paths: Path) -> list[str]:
    texts: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            texts.extend(p["text"] for p in yaml.safe_load(f)["prompts"])
    return texts


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    # Eval pack has length span; smoke claim remains tentative vs formal fit≠eval.
    prompts = _load_texts(ROOT / "prompts/eval_prompts.yaml")
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        gene = {**early, "n": 1, "temperature": 1e-6}
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 5252
        serial = score_serial_early(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            max_new=max_new,
            seed=claim,
        )
        serial["n_prompts"] = float(len(prompts))
        rows.append(
            tip_row("H-EARLY", f"HEARLY_bucket_seed{seed}", serial, seed, gene)
        )
        batched = score_batch_early(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            max_new=max_new,
            seed=claim,
        )
        batched["n_prompts"] = float(len(prompts))
        rows.append(tip_row("H-BAT", f"HBAT_bucket_seed{seed}", batched, seed, gene))
        bucketed = score_bucket_early(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            max_new=max_new,
            seed=claim,
            band=DEFAULT_BAND,
        )
        bucketed["n_prompts"] = float(len(prompts))
        row = tip_row(
            "H-BUCKET", f"HBUCKET_seed{seed}", bucketed, seed, gene
        )
        row["n_buckets"] = int(bucketed["n_buckets"])
        write_json(out / f"HBUCKET_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "bucket_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "band": DEFAULT_BAND,
            "mode": "n=1 near-greedy; eval pack",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "bucket_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
