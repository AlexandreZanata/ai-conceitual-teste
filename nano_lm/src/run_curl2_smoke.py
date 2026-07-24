"""Smoke H-CURL2: fine seq_lo∈{4,6,8,10,12} vs tip lo=8."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from curl2_ops import CURL2_LOS
from cur_ops import N_STAGES
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
        for seq_lo in CURL2_LOS:
            ckpt = out / f"HCURL2_lo{seq_lo}_seed{seed}.pt"
            # Reuse tip lo=8 smoke ckpt when present (same train recipe).
            tip8 = out / f"HCURL_lo8_seed{seed}.pt"
            if int(seq_lo) == 8 and tip8.is_file() and not ckpt.is_file():
                ckpt = tip8
            if not ckpt.is_file():
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
                    seed=seed + 41 * int(seq_lo),
                    temperature=2.0,
                    alpha=0.5,
                    out_path=ckpt,
                    seq_lo=int(seq_lo),
                    n_stages=N_STAGES,
                    hypothesis="H-CURL2",
                )
                write_json(
                    out / f"HCURL2_lo{seq_lo}_seed{seed}_train.json", meta
                )
            ev = eval_ckpt(c, ckpt, seed, "H-CURL2")
            ev["seq_lo"] = int(seq_lo)
            ev["label"] = f"HCURL2_lo{seq_lo}_seed{seed}"
            write_json(out / f"HCURL2_lo{seq_lo}_seed{seed}_eval.json", ev)
            rows.append(ev)
            if device.type == "cuda":
                torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    write_json(out / "curl2_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "curl2_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
