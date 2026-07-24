"""Formal-budget H-CURL2: fine seq_lo∈{4,6,8,10,12} vs tip lo=8."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from curl2_ops import CURL2_LOS
from cur_ops import N_STAGES
from hyp_cur import run_h_cur
from load_model import resolve_device
from matrix_common import ROOT, REPO, eval_ckpt, write_json
from run_formal_hcurl import formal_cfg as hcurl_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hcurl_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hcurl2"
    base["curl_dir"] = REPO / "results/nano-lm/formal-hcurl"
    return base


def run_formal() -> int:
    c = formal_cfg()
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    curl_dir: Path = c["curl_dir"]
    for seed in c["seeds"]:
        for seq_lo in CURL2_LOS:
            ckpt = c["out"] / f"HCURL2_lo{seq_lo}_seed{seed}.pt"
            tip8 = curl_dir / f"HCURL_lo8_seed{seed}.pt"
            if int(seq_lo) == 8:
                if not tip8.is_file():
                    raise FileNotFoundError(f"missing formal CURL tip: {tip8}")
                ckpt = tip8
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
                    seed=seed + 41 * int(seq_lo),
                    temperature=2.0,
                    alpha=0.5,
                    out_path=ckpt,
                    seq_lo=int(seq_lo),
                    n_stages=N_STAGES,
                    hypothesis="H-CURL2",
                )
                write_json(
                    c["out"] / f"HCURL2_lo{seq_lo}_seed{seed}_train.json", meta
                )
            ev = eval_ckpt(c, ckpt, seed, "H-CURL2")
            ev["seq_lo"] = int(seq_lo)
            ev["label"] = f"HCURL2_lo{seq_lo}_seed{seed}"
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
