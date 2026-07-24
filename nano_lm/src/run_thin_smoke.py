"""Smoke H-THIN: CURL-train thin student; claim with frozen EARLY genes."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from cur_ops import N_STAGES
from early_fit import fitness_early_detail
from eval_student import load_student_ckpt
from hyp_cur import run_h_cur
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from student_model import build_thin_student


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
    build_fn: Any,
) -> dict[str, Any]:
    student = load_student_ckpt(
        ckpt, teacher.tokenizer, teacher.device, build_fn=build_fn
    )
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
    }


def main() -> int:
    from student_model import build_student

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
    steps = int(c.get("steps_cur", c["steps_kd"]))
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        curl_ckpt = out / f"HCURL_lo8_seed{seed}.pt"
        if not curl_ckpt.is_file():
            raise FileNotFoundError(f"missing H-CURL tip ckpt: {curl_ckpt}")
        thin_ckpt = out / f"HTHIN_lo8_seed{seed}.pt"
        if not thin_ckpt.is_file():
            meta = run_h_cur(
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                cache_dir=c["cache"],
                device=device,
                steps=steps,
                batch_size=c["batch_size"],
                seq_len=c["seq_len"],
                max_examples=c["max_examples"],
                lr=c["lr"],
                seed=seed + 97,
                temperature=2.0,
                alpha=0.5,
                out_path=thin_ckpt,
                seq_lo=8,
                n_stages=N_STAGES,
                build_fn=build_thin_student,
                hypothesis="H-THIN",
            )
            write_json(out / f"HTHIN_lo8_seed{seed}_train.json", meta)
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
            build_fn=build_student,
        )
        thin_row = _score(
            family="H-THIN",
            label=f"HTHIN_lo8_early_seed{seed}",
            ckpt=thin_ckpt,
            gene=gene,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            build_fn=build_thin_student,
        )
        write_json(out / f"HTHIN_seed{seed}_eval.json", thin_row)
        rows.extend([curl_row, thin_row])
        if device.type == "cuda":
            torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    write_json(out / "thin_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "thin_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
