"""Formal-budget H-STAG: n_stages∈{2,3,4} under CURL2 seq_lo=6."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from hyp_cur import run_h_cur
from load_model import resolve_device
from matrix_common import REPO, eval_ckpt, write_json
from run_formal_hcurl2 import formal_cfg as hcurl2_formal_cfg
from stag_ops import STAG_SEQ_LO, STAG_STAGES


def formal_cfg() -> dict[str, Any]:
    base = hcurl2_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hstag"
    base["curl2_dir"] = REPO / "results/nano-lm/formal-hcurl2"
    return base


def run_formal() -> int:
    c = formal_cfg()
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    curl2_dir: Path = c["curl2_dir"]
    for seed in c["seeds"]:
        for n_stages in STAG_STAGES:
            ckpt = c["out"] / f"HSTAG_st{n_stages}_seed{seed}.pt"
            tip3 = curl2_dir / f"HCURL2_lo{STAG_SEQ_LO}_seed{seed}.pt"
            if int(n_stages) == 3:
                if not tip3.is_file():
                    raise FileNotFoundError(f"missing formal CURL2 tip: {tip3}")
                ckpt = tip3
            elif not ckpt.is_file():
                meta = run_h_cur(
                    teacher_id=c["teacher_id"],
                    tokenizer_id=c["tokenizer_id"],
                    cache_dir=c["cache"],
                    device=device,
                    steps=c["steps_kd"],
                    batch_size=c["batch_size"],
                    seq_len=c["seq_len"],
                    max_examples=c["max_examples"],
                    lr=c["lr"],
                    seed=seed + 47 * int(n_stages),
                    temperature=2.0,
                    alpha=0.5,
                    out_path=ckpt,
                    seq_lo=STAG_SEQ_LO,
                    n_stages=int(n_stages),
                    hypothesis="H-STAG",
                )
                write_json(
                    c["out"] / f"HSTAG_st{n_stages}_seed{seed}_train.json", meta
                )
            ev = eval_ckpt(c, ckpt, seed, "H-STAG")
            ev["n_stages"] = int(n_stages)
            ev["seq_lo"] = STAG_SEQ_LO
            ev["label"] = f"HSTAG_st{n_stages}_seed{seed}"
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
