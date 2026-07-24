"""Smoke H-CACHE: tip EARLY genes + KV decode vs EARLY/B4."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from cache_fit import fitness_cache_detail
from eval_student import load_student_ckpt
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _tip_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing H-EARLY tip gene: {path}")
    row = json.loads(path.read_text(encoding="utf-8"))
    gene = row.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"HEARLY tip missing best_gene: {path}")
    return gene


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    prompts = _prompts(c["prompts"])
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        gene = _tip_gene(out, seed)
        student = load_student_ckpt(ckpt, teacher.tokenizer, teacher.device)
        lp, wall = fitness_cache_detail(
            gene,
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=max_new,
            seed=seed + 7777,
        )
        row = {
            "family": "H-CACHE",
            "label": f"HCACHE_seed{seed}",
            "teacher_mean_logprob": float(lp),
            "mean_wall_ms": float(wall),
            "n_prompts": len(prompts),
            "seed": seed,
            "best_gene": gene,
            "ckpt_source": "B2",
            "gene_source": "H-EARLY tip",
            "use_kv_cache": True,
        }
        write_json(out / f"HCACHE_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "cache_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "cache_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
