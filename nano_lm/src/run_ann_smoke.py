"""Smoke H-ANN vs KD-cos on same budget; merge into matrix.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_ann import run_h_ann, run_kd_cosine
from load_model import resolve_device
from matrix_common import eval_ckpt, matrix_cfg, write_json


def _merge(rows: list[dict[str, Any]], wall_s: float, out: Path) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    drop = {"H-ANN", "KD-cos"}
    kept = [r for r in data.get("rows", []) if r.get("family") not in drop]
    data["rows"] = kept + rows
    data["ann_wall_s"] = wall_s
    write_json(path, data)


def _train_eval(
    c: dict[str, Any],
    device: Any,
    *,
    seed: int,
    schedule_fn: Any,
    family: str,
    prefix: str,
) -> dict[str, Any]:
    out: Path = c["out"]
    ckpt = out / f"{prefix}_seed{seed}.pt"
    meta = schedule_fn(
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        device=device,
        steps=int(c.get("steps_ann", c["steps_kd"])),
        batch_size=c["batch_size"],
        seq_len=c["seq_len"],
        max_examples=c["max_examples"],
        lr=c["lr"],
        seed=seed,
        temperature=float(c.get("ann_temp_start", 2.0)),
        alpha=0.5,
        out_path=ckpt,
        temp_end=float(c.get("ann_temp_end", 1.0)),
    )
    write_json(out / f"{prefix}_seed{seed}_train.json", meta)
    ev = eval_ckpt(c, ckpt, seed, family)
    write_json(out / f"{prefix}_seed{seed}_eval.json", ev)
    return ev


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.append(
            _train_eval(
                c, device, seed=seed, schedule_fn=run_kd_cosine, family="KD-cos", prefix="KDCOS"
            )
        )
        rows.append(
            _train_eval(
                c, device, seed=seed, schedule_fn=run_h_ann, family="H-ANN", prefix="HANN"
            )
        )
    wall_s = time.perf_counter() - t0
    write_json(c["out"] / "ann_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge(rows, wall_s, c["out"])
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "ann_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
