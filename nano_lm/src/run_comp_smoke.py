"""Smoke H-COMP: torch.compile on B2 + frozen EARLY tip genes."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from comp_ops import COMPILE_MODE, compile_student, warmup_student
from early_fit import fitness_early_detail
from eval_student import load_student_ckpt
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing H-EARLY tip gene: {path}")
    row = json.loads(path.read_text(encoding="utf-8"))
    gene = row.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"HEARLY tip missing best_gene: {path}")
    return gene


def _score(
    *,
    family: str,
    label: str,
    ckpt: Path,
    gene: dict[str, Any],
    teacher: Any,
    prompts: list[str],
    max_new: int,
    seed: int,
    compiled: bool,
) -> dict[str, Any]:
    device = teacher.device
    student = load_student_ckpt(ckpt, teacher.tokenizer, device)
    if compiled:
        student = compile_student(student, mode=COMPILE_MODE)
        warmup_student(student, device, steps=3)
    lp, wall = fitness_early_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 7777,
    )
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "n_prompts": len(prompts),
        "seed": seed,
        "best_gene": gene,
        "ckpt": str(ckpt),
        "compiled": compiled,
        "compile_mode": COMPILE_MODE if compiled else "eager",
    }


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; compile may not help", file=sys.stderr)
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
        gene = _early_gene(out, seed)
        early_row = _score(
            family="H-EARLY",
            label=f"HEARLY_eager_seed{seed}",
            ckpt=ckpt,
            gene=gene,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            compiled=False,
        )
        comp_row = _score(
            family="H-COMP",
            label=f"HCOMP_seed{seed}",
            ckpt=ckpt,
            gene=gene,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            compiled=True,
        )
        write_json(out / f"HCOMP_seed{seed}_eval.json", comp_row)
        rows.extend([early_row, comp_row])
        if device.type == "cuda":
            torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    write_json(out / "comp_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "comp_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
