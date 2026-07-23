"""Smoke H-DIF discrete diffusion vs B2; merge into matrix.json."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_dif import run_h_dif
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def _merge(rows: list[dict[str, Any]], wall_s: float, out: Path) -> None:
    path = out / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    kept = [r for r in data.get("rows", []) if r.get("family") != "H-DIF"]
    data["rows"] = kept + rows
    data["dif_wall_s"] = wall_s
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
    steps = int(c.get("steps_dif", c["steps_kd"]))
    dif_steps = int(c.get("dif_steps", 4))
    for seed in c["seeds"]:
        ckpt = out / f"HDIF_seed{seed}.pt"
        meta = run_h_dif(
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
            out_path=ckpt,
            dif_steps=dif_steps,
            prompts_path=c["prompts"],
            max_new_eval=int(c["max_new_eval"]),
        )
        write_json(out / f"HDIF_seed{seed}_train.json", meta)
        row = {
            "family": "H-DIF",
            "label": f"HDIF_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "peak_vram_mib": float(meta["peak_vram_mib"]),
            "n_prompts": 2,
            "seed": seed,
            "dif_steps": dif_steps,
        }
        write_json(out / f"HDIF_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "dif_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge(rows, wall_s, out)
    print(json.dumps({"n_rows": len(rows), "out": str(out / "dif_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
