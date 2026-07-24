"""Smoke H-ALAT (αT): scheduled KD α/T under CURL2 vs tip lo=6."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from cur_ops import N_STAGES
from hyp_alat import run_h_alat
from hyp_cur import run_h_cur
from load_model import resolve_device
from matrix_common import eval_ckpt, matrix_cfg, write_json

TIP_LO = 6


def _ensure_tip(c: dict, out: Path, device, seed: int, steps: int) -> Path:
    tip = out / f"HCURL2_lo{TIP_LO}_seed{seed}.pt"
    if tip.is_file():
        return tip
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
    return tip


def _train_alat(c: dict, out: Path, device, seed: int, steps: int) -> Path:
    ckpt = out / f"HALAT_seed{seed}.pt"
    if ckpt.is_file():
        return ckpt
    meta = run_h_alat(
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        device=device,
        steps=steps,
        batch_size=c["batch_size"],
        seq_len=c["seq_len"],
        max_examples=c["max_examples"],
        lr=c["lr"],
        seed=seed + 83,
        out_path=ckpt,
        seq_lo=TIP_LO,
        n_stages=N_STAGES,
    )
    write_json(out / f"HALAT_seed{seed}_train.json", meta)
    return ckpt


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
        tip = _ensure_tip(c, out, device, seed, steps)
        tip_ev = eval_ckpt(c, tip, seed, "H-CURL2")
        tip_ev.update(seq_lo=TIP_LO, label=f"HCURL2_lo{TIP_LO}_seed{seed}")
        rows.append(tip_ev)
        ckpt = _train_alat(c, out, device, seed, steps)
        ev = eval_ckpt(c, ckpt, seed, "H-ALAT")
        ev["label"] = f"HALAT_seed{seed}"
        write_json(out / f"HALAT_seed{seed}_eval.json", ev)
        rows.append(ev)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    write_json(
        out / "alat_smoke.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "alat_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
