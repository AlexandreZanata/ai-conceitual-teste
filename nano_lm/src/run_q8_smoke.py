"""Smoke H-Q8: INT8 dynamic quant on CURL ckpt; claim with EARLY genes."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from early_fit import fitness_early_detail
from eval_student import load_student_ckpt
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from q8_ops import quantize_student_dynamic


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
    quantize: bool,
) -> dict[str, Any]:
    device = teacher.device
    student = load_student_ckpt(ckpt, teacher.tokenizer, device)
    student_device = device
    if quantize:
        student = quantize_student_dynamic(student)
        student_device = torch.device("cpu")
    lp, wall = fitness_early_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 7777,
        student_device=student_device,
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
        "quantize": quantize,
        "student_device": str(student_device),
    }


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; tip control on CPU", file=sys.stderr)
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
        curl_ckpt = out / f"HCURL_lo8_seed{seed}.pt"
        if not curl_ckpt.is_file():
            raise FileNotFoundError(f"missing H-CURL tip ckpt: {curl_ckpt}")
        gene = _early_gene(out, seed)
        curl_row = _score(
            family="H-CURL",
            label=f"HCURL_lo8_early_seed{seed}",
            ckpt=curl_ckpt,
            gene=gene,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            quantize=False,
        )
        q8_row = _score(
            family="H-Q8",
            label=f"HQ8_lo8_early_seed{seed}",
            ckpt=curl_ckpt,
            gene=gene,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            quantize=True,
        )
        write_json(out / f"HQ8_seed{seed}_eval.json", q8_row)
        rows.extend([curl_row, q8_row])
        if device.type == "cuda":
            torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    write_json(out / "q8_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "q8_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
