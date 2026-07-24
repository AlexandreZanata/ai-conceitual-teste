"""Smoke H-CURT (adopted n=5, lo=8) vs H-CUR tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from curt_ops import CURT_SEQ_LO, CURT_STAGES
from hyp_cur import run_h_cur
from load_model import resolve_device
from matrix_common import eval_ckpt, matrix_cfg, write_json


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
        ckpt = out / f"HCURT_seed{seed}.pt"
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
            seed=seed + 101,
            temperature=2.0,
            alpha=0.5,
            out_path=ckpt,
            seq_lo=CURT_SEQ_LO,
            n_stages=CURT_STAGES,
        )
        write_json(out / f"HCURT_seed{seed}_train.json", meta)
        ev = eval_ckpt(c, ckpt, seed, "H-CURT")
        ev["seq_lo"] = CURT_SEQ_LO
        ev["n_stages"] = CURT_STAGES
        write_json(out / f"HCURT_seed{seed}_eval.json", ev)
        rows.append(ev)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    write_json(out / "curt_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "curt_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
