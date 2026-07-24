"""Smoke H-QG: quality-gated FLOP min vs frozen H-EARLY tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from earf_fit import fitness_earf_detail
from eval_student import load_student_ckpt
from hyp_qg import run_h_qg
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json


def _tip_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _row(
    family: str,
    label: str,
    lp: float,
    wall: float,
    gflops: float,
    seed: int,
    gene: dict[str, Any],
    empty_rate: float = 0.0,
) -> dict[str, Any]:
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
        "mean_est_gflops": float(gflops),
        "empty_rate": float(empty_rate),
        "n_prompts": 2,
        "seed": seed,
        "best_gene": gene,
    }


def _score_tip(
    out: Path, teacher, prompts: list[str], max_new: int, seed: int
) -> tuple[dict[str, Any], dict[str, Any]]:
    ckpt = out / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
    student = load_student_ckpt(ckpt, teacher.tokenizer, teacher.device)
    gene = _tip_gene(out, seed)
    lp, wall, gf = fitness_earf_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=seed + 7777,
    )
    return _row("H-EARLY", f"HEARLY_qg_seed{seed}", lp, wall, gf, seed, gene), gene


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
    with c["prompts"].open(encoding="utf-8") as f:
        prompts = [p["text"] for p in yaml.safe_load(f)["prompts"]]
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        tip_row, tip_gene = _score_tip(out, teacher, prompts, max_new, seed)
        rows.append(tip_row)
        meta = run_h_qg(
            student_ckpt=out / f"B2_seed{seed}.pt",
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=4,
            generations=2,
            max_new=min(16, max_new),
            eval_max_new=max_new,
            seed=seed,
            tip_gene=tip_gene,
            out_meta=out / f"HQG_seed{seed}_train.json",
        )
        row = _row(
            "H-QG",
            f"HQG_seed{seed}",
            float(meta["eval_fit"]),
            float(meta["eval_wall_ms"]),
            float(meta["eval_est_gflops"]),
            seed,
            meta["best_gene"],
            empty_rate=float(meta["empty_rate"]),
        )
        write_json(out / f"HQG_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "qg_smoke.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "qg_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
