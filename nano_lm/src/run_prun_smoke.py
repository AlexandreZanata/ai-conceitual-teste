"""Smoke H-PRUN: magnitude prune STAG → recovery KD; EARLY claim vs tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from eval_student import load_student_ckpt
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from prun_fit import row, score_early_flops
from prun_mask import sparsity_of
from prun_ops import DEFAULT_SPARSITY
from prun_recover import recover_pruned_kd

RECOVER_STEPS = 20
TIP_STAGES = 4


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _run_seed(
    c: dict[str, Any],
    out: Path,
    seed: int,
    teacher,
    prompts: list[str],
    max_new: int,
) -> list[dict[str, Any]]:
    early = _early_gene(out, seed)
    tip_ckpt = out / f"HSTAG_st{TIP_STAGES}_seed{seed}.pt"
    if not tip_ckpt.is_file():
        raise FileNotFoundError(f"missing STAG tip: {tip_ckpt}")
    tip_student = load_student_ckpt(tip_ckpt, teacher.tokenizer, teacher.device)
    claim = seed + 7777
    lp_t, wall_t, gf_t = score_early_flops(
        early,
        teacher=teacher,
        student=tip_student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        density=1.0,
    )
    tip_row = row(
        "H-STAG",
        f"HSTAG_prun_seed{seed}",
        lp_t,
        wall_t,
        gf_t,
        seed,
        {"density": 1.0, "best_gene": early},
    )
    student = load_student_ckpt(tip_ckpt, teacher.tokenizer, teacher.device)
    prun_ckpt = out / f"HPRUN_seed{seed}.pt"
    meta = recover_pruned_kd(
        student=student,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        device=teacher.device,
        steps=RECOVER_STEPS,
        batch_size=int(c["batch_size"]),
        seq_len=int(c["seq_len"]),
        max_examples=int(c["max_examples"]),
        lr=float(c["lr"]),
        seed=seed + 17,
        temperature=2.0,
        alpha=0.5,
        sparsity=DEFAULT_SPARSITY,
        out_path=prun_ckpt,
    )
    write_json(out / f"HPRUN_seed{seed}_train.json", meta)
    dens = float(meta["density"])
    lp_p, wall_p, gf_p = score_early_flops(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        density=dens,
    )
    prun_row = row(
        "H-PRUN",
        f"HPRUN_seed{seed}",
        lp_p,
        wall_p,
        gf_p,
        seed,
        {
            "density": dens,
            "sparsity": sparsity_of(student),
            "best_gene": early,
        },
    )
    write_json(out / f"HPRUN_seed{seed}_eval.json", prun_row)
    return [tip_row, prun_row]


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = _prompts(c["prompts"])
    max_new = int(c["max_new_eval"])
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, out, seed, teacher, prompts, max_new))
    write_json(
        out / "prun_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "sparsity_target": DEFAULT_SPARSITY,
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "prun_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
