"""Smoke H-FLASH: SDPA backend vs eager H-EARLY tip (same genes)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from eval_decode import load_pair
from flash_fit import fitness_flash_detail, tip_row
from flop_score import load_prompts
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from short_fit import fitness_early_detail


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
        print("WARN: CUDA unavailable; SDPA may use math kernel", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = [p["text"] for p in load_prompts(c["prompts"])]
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 8080
        lp_e, wall_e, gf_e = fitness_early_detail(
            early,
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=max_new,
            seed=claim,
        )
        rows.append(
            tip_row(
                "H-EARLY", f"HEARLY_flash_seed{seed}", lp_e, wall_e, gf_e, seed, early
            )
        )
        lp_f, wall_f, gf_f = fitness_flash_detail(
            early,
            teacher=teacher,
            student=student,
            prompts=prompts,
            max_new=max_new,
            seed=claim,
        )
        row = tip_row(
            "H-FLASH", f"HFLASH_seed{seed}", lp_f, wall_f, gf_f, seed, early
        )
        write_json(out / f"HFLASH_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "flash_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "backend": "gpt_neo_sdpa",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "flash_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
