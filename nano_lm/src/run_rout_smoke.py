"""Smoke H-ROUT on B2 ckpts; dual gate vs H-EARLY + H-DECM tip genes."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_rout import run_h_rout
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from rout_ops import DEFAULT_TAU


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    tau = float(c.get("rout_tau", DEFAULT_TAU))
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        early_meta = out / f"HEARLY_seed{seed}_train.json"
        decm_meta = out / f"HDECM_seed{seed}_train.json"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        if not early_meta.is_file() or not decm_meta.is_file():
            raise FileNotFoundError("missing HEARLY/HDECM tip gene train json")
        meta = run_h_rout(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            early_gene_path=early_meta,
            decm_gene_path=decm_meta,
            max_new=int(c["max_new_eval"]),
            seed=seed,
            tau=tau,
            out_meta=out / f"HROUT_seed{seed}_train.json",
        )
        row = {
            "family": "H-ROUT",
            "label": f"HROUT_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "early_rate": float(meta["early_rate"]),
            "n_prompts": 2,
            "seed": seed,
            "tau": tau,
            "routes": meta["routes"],
        }
        write_json(out / f"HROUT_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "rout_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "rout_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
