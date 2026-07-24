"""Smoke H-REP: rep-penalty / no-repeat under frozen H-EARLY tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from eval_decode import load_pair
from flop_score import load_prompts
from hyp_rep import run_h_rep
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from rep_fit import fitness_early_detail, fitness_rep_detail, tip_row

LAM = 0.4


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = load_prompts(c["prompts"])
    prompt_texts = [p["text"] for p in prompts]
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        meta = run_h_rep(
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
            early_gene=early,
            lam=LAM,
            out_meta=out / f"HREP_seed{seed}_train.json",
        )
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 6060
        lp_e, wall_e, gf_e = fitness_early_detail(
            early,
            teacher=teacher,
            student=student,
            prompts=prompt_texts,
            max_new=max_new,
            seed=claim,
        )
        rows.append(
            tip_row("H-EARLY", f"HEARLY_rep_seed{seed}", lp_e, wall_e, gf_e, seed, early)
        )
        lp_r, wall_r, gf_r = fitness_rep_detail(
            meta["best_gene"],
            early,
            teacher=teacher,
            student=student,
            prompts=prompt_texts,
            max_new=max_new,
            seed=claim,
        )
        row = tip_row(
            "H-REP", f"HREP_seed{seed}", lp_r, wall_r, gf_r, seed, meta["best_gene"]
        )
        write_json(out / f"HREP_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "rep_smoke.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0, "lam": LAM},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "rep_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
