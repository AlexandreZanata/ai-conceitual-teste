"""Smoke H-TYP on B2 ckpts; dual gate vs B4 (matrix)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_typ import run_h_typ
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        meta = run_h_typ(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            max_new=int(c["max_new_eval"]),
            seed=seed,
            out_meta=out / f"HTYP_seed{seed}_train.json",
        )
        row = {
            "family": "H-TYP",
            "label": f"HTYP_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "best_typ_mass": float(meta["best_typ_mass"]),
            "n_prompts": 2,
            "seed": seed,
        }
        write_json(out / f"HTYP_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "typ_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "typ_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
