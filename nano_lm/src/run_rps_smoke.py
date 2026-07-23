"""Smoke H-RPS on matrix out dir; merge rows into matrix.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_rps import run_h_rps
from load_model import resolve_device
from matrix_common import eval_ckpt, matrix_cfg, write_json


def _merge(rows: list[dict[str, Any]], wall_s: float, out: Path) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    kept = [r for r in data.get("rows", []) if r.get("family") != "H-RPS"]
    data["rows"] = kept + rows
    data["rps_wall_s"] = wall_s
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
    for seed in c["seeds"]:
        ckpt = out / f"HRPS_seed{seed}.pt"
        meta = run_h_rps(
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            pop_size=4,
            generations=3,
            mutate_scale=0.02,
            seq_len=c["seq_len"],
            batch_size=c["batch_size"],
            max_examples=c["max_examples"],
            seed=seed,
            out_path=ckpt,
        )
        write_json(out / f"HRPS_seed{seed}_train.json", meta)
        ev = eval_ckpt(c, ckpt, seed, "H-RPS")
        ev["niche_collapsed"] = bool(meta.get("niche_collapsed"))
        write_json(out / f"HRPS_seed{seed}_eval.json", ev)
        rows.append(ev)
    wall_s = time.perf_counter() - t0
    write_json(out / "rps_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge(rows, wall_s, out)
    print(json.dumps({"n_rows": len(rows), "out": str(out / "rps_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
