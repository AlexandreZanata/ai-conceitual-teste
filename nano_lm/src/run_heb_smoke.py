"""Smoke H-HEB (KD + local Hebb) vs B2; merge into matrix.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_heb import run_h_heb
from load_model import resolve_device
from matrix_common import eval_ckpt, matrix_cfg, write_json


def _merge(rows: list[dict[str, Any]], wall_s: float, out: Path) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    kept = [r for r in data.get("rows", []) if r.get("family") != "H-HEB"]
    data["rows"] = kept + rows
    data["heb_wall_s"] = wall_s
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
    steps = int(c.get("steps_heb", c["steps_kd"]))
    for seed in c["seeds"]:
        ckpt = out / f"HHEB_seed{seed}.pt"
        meta = run_h_heb(
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
            out_path=ckpt,
            heb_eta=float(c.get("heb_eta", 1e-4)),
        )
        write_json(out / f"HHEB_seed{seed}_train.json", meta)
        ev = eval_ckpt(c, ckpt, seed, "H-HEB")
        ev["diverged"] = 1.0 if meta["diverged"] else 0.0
        ev["unstable"] = bool(meta["diverged"])
        write_json(out / f"HHEB_seed{seed}_eval.json", ev)
        rows.append(ev)
    wall_s = time.perf_counter() - t0
    write_json(out / "heb_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge(rows, wall_s, out)
    print(json.dumps({"n_rows": len(rows), "out": str(out / "heb_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
