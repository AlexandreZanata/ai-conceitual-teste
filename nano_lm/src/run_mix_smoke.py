"""Smoke H-MIX: PRUN ckpt ⊕ LAY decode vs PRUN+EARLY (protocol, not tip)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from eval_student import load_student_ckpt
from flop_score import load_prompts
from lay_fit import fitness_lay_detail, tip_row
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from prun_fit import score_early_flops
from prun_mask import density_of


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _lay_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HLAY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing LAY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"LAY missing best_gene: {path}")
    return gene


def _run_seed(
    c: dict[str, Any],
    out: Path,
    seed: int,
    teacher,
    prompts: list[str],
    max_new: int,
) -> list[dict[str, Any]]:
    early = _early_gene(out, seed)
    lay = _lay_gene(out, seed)
    prun_ckpt = out / f"HPRUN_seed{seed}.pt"
    if not prun_ckpt.is_file():
        raise FileNotFoundError(f"missing PRUN ckpt: {prun_ckpt}")
    student = load_student_ckpt(prun_ckpt, teacher.tokenizer, teacher.device)
    dens = density_of(student)
    claim = seed + 5555
    lp_p, wall_p, gf_p = score_early_flops(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        density=dens,
    )
    prun_row = tip_row(
        "H-PRUN",
        f"HPRUN_mix_seed{seed}",
        lp_p,
        wall_p,
        gf_p,
        seed,
        {**early, "density": dens},
    )
    prun_row["density"] = dens
    lp_m, wall_m, gf_m = fitness_lay_detail(
        lay,
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    gf_m = float(gf_m) * float(dens)
    mix_row = tip_row(
        "H-MIX",
        f"HMIX_seed{seed}",
        lp_m,
        wall_m,
        gf_m,
        seed,
        {**early, **lay, "density": dens},
    )
    mix_row["density"] = dens
    write_json(out / f"HMIX_seed{seed}_eval.json", mix_row)
    return [prun_row, mix_row]


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = [p["text"] for p in load_prompts(c["prompts"])]
    max_new = int(c["max_new_eval"])
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, out, seed, teacher, prompts, max_new))
    write_json(
        out / "mix_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "note": "protocol stack; not a tip H-ID",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "mix_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
