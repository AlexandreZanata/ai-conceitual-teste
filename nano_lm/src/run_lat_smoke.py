"""Smoke H-LAT on B2 checkpoints; merge into matrix.json vs B4."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_lat import run_h_lat
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def _merge(rows: list[dict[str, Any]], wall_s: float, out: Path) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    kept = [r for r in data.get("rows", []) if r.get("family") != "H-LAT"]
    data["rows"] = kept + rows
    data["lat_wall_s"] = wall_s
    write_json(path, data)


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    lam = float(c.get("lat_lam", 0.15))
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        meta = run_h_lat(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=4,
            generations=2,
            max_new=min(16, int(c["max_new_eval"])),
            eval_max_new=int(c["max_new_eval"]),
            seed=seed,
            lam=lam,
            out_meta=out / f"HLAT_seed{seed}_train.json",
        )
        row = {
            "family": "H-LAT",
            "label": f"HLAT_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "search_fit": float(meta["best_fit"]),
            "n_prompts": 2,
            "seed": seed,
            "best_gene": meta["best_gene"],
            "lam": lam,
        }
        write_json(out / f"HLAT_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "lat_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge(rows, wall_s, out)
    print(json.dumps({"n_rows": len(rows), "out": str(out / "lat_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
