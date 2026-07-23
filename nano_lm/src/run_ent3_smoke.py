"""Smoke H-ENT3 dual-head disagreement + mix KD; merge into matrix.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_ent3 import eval_ent3_vs_teacher, run_h_ent3
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def _merge(rows: list[dict[str, Any]], wall_s: float, out: Path) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    kept = [r for r in data.get("rows", []) if r.get("family") != "H-ENT3"]
    data["rows"] = kept + rows
    data["ent3_wall_s"] = wall_s
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
    steps = int(c.get("steps_ent", c["steps_kd"]))
    disagree = float(c.get("disagree_weight", 0.1))
    for seed in c["seeds"]:
        ckpt = out / f"HENT3_seed{seed}.pt"
        meta = run_h_ent3(
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            steps=steps,
            batch_size=c["batch_size"],
            seq_len=c["seq_len"],
            max_examples=c["max_examples"],
            lr=c["lr"],
            seed=seed,
            temperature=2.0,
            alpha=0.5,
            disagree_weight=disagree,
            noise_std=0.01,
            out_path=ckpt,
        )
        write_json(out / f"HENT3_seed{seed}_train.json", meta)
        ev = eval_ent3_vs_teacher(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            max_new_tokens=c["max_new_eval"],
            seed=seed,
            temperature=0.8,
            top_p=0.9,
        )
        ev["family"] = "H-ENT3"
        ev["heads_collapsed"] = bool(meta.get("heads_collapsed"))
        ev["mode_chaos"] = bool(meta.get("mode_chaos"))
        ev["mean_tv"] = float(meta.get("mean_tv", 0.0))
        write_json(out / f"HENT3_seed{seed}_eval.json", ev)
        rows.append(ev)
    wall_s = time.perf_counter() - t0
    write_json(out / "ent3_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge(rows, wall_s, out)
    print(json.dumps({"n_rows": len(rows), "out": str(out / "ent3_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
