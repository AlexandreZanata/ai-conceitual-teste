"""Smoke H-CAP: hard max_new/n on H-POOL tip genes."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from cap_ops import CAP_NEWS, apply_hard_caps
from dec_fit_ops import fitness_gene_detail
from eval_student import load_student_ckpt
from lat2_ops import MIN_LAM
from lat_ops import latency_aware_score
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _tip_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HPOOL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing H-POOL tip gene: {path}")
    row = json.loads(path.read_text(encoding="utf-8"))
    gene = row.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"HPOOL tip missing best_gene: {path}")
    return gene


def _pick_cap(
    gene: dict[str, Any],
    *,
    teacher: Any,
    student: Any,
    prompts: list[str],
    seed: int,
) -> tuple[dict[str, Any], int, float, float]:
    best: tuple[float, dict, int, float, float] | None = None
    for raw in CAP_NEWS:
        g, mn = apply_hard_caps(gene, raw)
        lp, wall = fitness_gene_detail(
            g,
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=mn,
            seed=seed + 7777,
        )
        score = latency_aware_score(lp, wall, MIN_LAM)
        if best is None or score > best[0]:
            best = (score, g, mn, lp, wall)
    assert best is not None
    _, g, mn, lp, wall = best
    return g, mn, lp, wall


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
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        tip = _tip_gene(out, seed)
        student = load_student_ckpt(ckpt, teacher.tokenizer, teacher.device)
        gene, max_new, lp, wall = _pick_cap(
            tip, teacher=teacher, student=student, prompts=prompts, seed=seed
        )
        row = {
            "family": "H-CAP",
            "label": f"HCAP_seed{seed}",
            "teacher_mean_logprob": float(lp),
            "mean_wall_ms": float(wall),
            "n_prompts": len(prompts),
            "seed": seed,
            "best_gene": gene,
            "max_new_cap": int(max_new),
            "ckpt_source": "B2",
            "gene_source": "H-POOL tip",
            "lam": MIN_LAM,
        }
        write_json(out / f"HCAP_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "cap_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "cap_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
