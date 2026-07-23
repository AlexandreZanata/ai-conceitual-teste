"""Smoke H-HOLD on matrix out dir; merge rows into matrix.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hold_ops import attach_overfit
from hyp_hold import run_h_hold
from load_model import resolve_device
from matrix_common import ROOT, eval_ckpt, matrix_cfg, write_json


def _merge(rows: list[dict[str, Any]], wall_s: float, out: Path) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    kept = [r for r in data.get("rows", []) if r.get("family") != "H-HOLD"]
    data["rows"] = kept + rows
    data["hold_wall_s"] = wall_s
    write_json(path, data)


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    fit_path = ROOT / "prompts/fit_prompts.yaml"
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    max_new_fit = int(c.get("max_new_fit", 16))
    for seed in c["seeds"]:
        ckpt = out / f"HHOLD_seed{seed}.pt"
        meta = run_h_hold(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            fit_prompts_path=fit_path,
            eval_prompts_path=c["prompts"],
            cache_dir=c["cache"],
            device=device,
            pop_size=4,
            generations=3,
            mutate_scale=0.02,
            max_new_fit=max_new_fit,
            seed=seed,
            out_path=ckpt,
        )
        write_json(out / f"HHOLD_seed{seed}_train.json", meta)
        row = eval_ckpt(c, ckpt, seed, "H-HOLD")
        attach_overfit(row, float(meta["best_fit"]))
        rows.append(row)
        write_json(out / f"HHOLD_seed{seed}_eval.json", rows[-1])
    wall_s = time.perf_counter() - t0
    write_json(out / "hold_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge(rows, wall_s, out)
    print(json.dumps({"n_rows": len(rows), "out": str(out / "hold_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
