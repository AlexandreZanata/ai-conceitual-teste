"""Formal-budget H-CURD vs H-CURL2 tip lo=6."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from cur_ops import N_STAGES
from hyp_curd import run_h_curd
from load_model import resolve_device
from matrix_common import ROOT, REPO, eval_ckpt, write_json
from run_formal_hcurl import formal_cfg as hcurl_formal_cfg

TIP_LO = 6


def formal_cfg() -> dict[str, Any]:
    base = hcurl_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hcurd"
    base["curl2_dir"] = REPO / "results/nano-lm/formal-hcurl2"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
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
        tip_ev["seq_lo"] = TIP_LO
        tip_ev["label"] = f"HCURL2_lo{TIP_LO}_seed{seed}"
        rows.append(tip_ev)
        curd = c["out"] / f"HCURD_seed{seed}.pt"
        if not curd.is_file():
            meta = run_h_curd(
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                cache_dir=c["cache"],
                device=device,
                steps=c["steps_kd"],
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
            write_json(c["out"] / f"HCURD_seed{seed}_train.json", meta)
        ev = eval_ckpt(c, curd, seed, "H-CURD")
        ev["label"] = f"HCURD_seed{seed}"
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
