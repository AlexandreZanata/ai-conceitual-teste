"""Formal-budget H-ALAT vs H-CURL2 tip lo=6."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from cur_ops import N_STAGES
from hyp_alat import run_h_alat
from load_model import resolve_device
from matrix_common import REPO, eval_ckpt, write_json
from run_formal_hcurl import formal_cfg as hcurl_formal_cfg

TIP_LO = 6


def formal_cfg() -> dict[str, Any]:
    base = hcurl_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-halat"
    base["curl2_dir"] = REPO / "results/nano-lm/formal-hcurl2"
    return base


def run_formal() -> int:
    c = formal_cfg()
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    curl2: Path = c["curl2_dir"]
    for seed in c["seeds"]:
        tip = curl2 / f"HCURL2_lo{TIP_LO}_seed{seed}.pt"
        if not tip.is_file():
            raise FileNotFoundError(f"missing formal CURL2 tip: {tip}")
        tip_ev = eval_ckpt(c, tip, seed, "H-CURL2")
        tip_ev.update(seq_lo=TIP_LO, label=f"HCURL2_lo{TIP_LO}_seed{seed}")
        rows.append(tip_ev)
        ckpt = c["out"] / f"HALAT_seed{seed}.pt"
        if not ckpt.is_file():
            meta = run_h_alat(
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                cache_dir=c["cache"],
                device=device,
                steps=c["steps_kd"],
                batch_size=c["batch_size"],
                seq_len=c["seq_len"],
                max_examples=c["max_examples"],
                lr=c["lr"],
                seed=seed + 83,
                out_path=ckpt,
                seq_lo=TIP_LO,
                n_stages=N_STAGES,
            )
            write_json(c["out"] / f"HALAT_seed{seed}_train.json", meta)
        ev = eval_ckpt(c, ckpt, seed, "H-ALAT")
        ev["label"] = f"HALAT_seed{seed}"
        rows.append(ev)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in c.items()},
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
