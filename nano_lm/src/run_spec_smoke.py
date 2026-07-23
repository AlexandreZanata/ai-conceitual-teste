"""Smoke B3/B4/H-SPEC on B2 checkpoints; merge into matrix.json when present."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from matrix_decode import run_decode_ops
from train_kd import train_kd


def _ensure_b2(c: dict[str, Any], device: Any) -> None:
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if ckpt.is_file():
            continue
        meta = train_kd(
            teacher_id=c["teacher_id"],
            steps=c["steps_kd"],
            batch_size=c["batch_size"],
            seq_len=c["seq_len"],
            max_examples=c["max_examples"],
            lr=c["lr"],
            seed=seed,
            temperature=2.0,
            alpha=0.5,
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            out_path=ckpt,
        )
        write_json(out / f"B2_seed{seed}_train.json", meta)


def _merge_matrix(out: Path, new_rows: list[dict[str, Any]], wall_s: float) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(
            path,
            {"rows": new_rows, "wall_s": wall_s, "config": {"note": "spec-only"}},
        )
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    drop = {"B3", "B4", "H-SPEC"}
    kept = [r for r in data.get("rows", []) if r.get("family") not in drop]
    data["rows"] = kept + new_rows
    data["spec_wall_s"] = wall_s
    write_json(path, data)


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    _ensure_b2(c, device)
    run_decode_ops(c, rows)
    wall_s = time.perf_counter() - t0
    write_json(c["out"] / "spec_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge_matrix(c["out"], rows, wall_s)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "spec_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
