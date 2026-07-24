"""Smoke H-CURD: teacher-NLL difficulty curriculum vs H-CURL2 tip lo=6."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from cur_ops import N_STAGES
from hyp_cur import run_h_cur
from hyp_curd import run_h_curd
from load_model import resolve_device
from matrix_common import eval_ckpt, matrix_cfg, write_json

TIP_LO = 6


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    steps = int(c.get("steps_cur", c["steps_kd"]))
    for seed in c["seeds"]:
        tip = out / f"HCURL2_lo{TIP_LO}_seed{seed}.pt"
        if not tip.is_file():
            meta = run_h_cur(
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                cache_dir=c["cache"],
                device=device,
                steps=steps,
                batch_size=c["batch_size"],
                seq_len=c["seq_len"],
                max_examples=c["max_examples"],
                lr=c["lr"],
                seed=seed + 41 * TIP_LO,
                temperature=2.0,
                alpha=0.5,
                out_path=tip,
                seq_lo=TIP_LO,
                n_stages=N_STAGES,
                hypothesis="H-CURL2",
            )
            write_json(out / f"HCURL2_lo{TIP_LO}_seed{seed}_train.json", meta)
        tip_ev = eval_ckpt(c, tip, seed, "H-CURL2")
        tip_ev["seq_lo"] = TIP_LO
        tip_ev["label"] = f"HCURL2_lo{TIP_LO}_seed{seed}"
        rows.append(tip_ev)
        curd = out / f"HCURD_seed{seed}.pt"
        if not curd.is_file():
            meta = run_h_curd(
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                cache_dir=c["cache"],
                device=device,
                steps=steps,
                batch_size=c["batch_size"],
                seq_len=c["seq_len"],
                max_examples=c["max_examples"],
                lr=c["lr"],
                seed=seed + 53,
                temperature=2.0,
                alpha=0.5,
                out_path=curd,
                n_stages=N_STAGES,
            )
            write_json(out / f"HCURD_seed{seed}_train.json", meta)
        ev = eval_ckpt(c, curd, seed, "H-CURD")
        ev["label"] = f"HCURD_seed{seed}"
        write_json(out / f"HCURD_seed{seed}_eval.json", ev)
        rows.append(ev)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    write_json(out / "curd_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "curd_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
