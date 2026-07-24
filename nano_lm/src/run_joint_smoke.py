"""Smoke H-JOINT: joint curriculum∪early search vs CURL+EARLY."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_joint import run_h_joint
from lat2_ops import MIN_LAM
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        meta = run_h_joint(
            c=c,
            device=device,
            seed=seed,
            out_dir=out,
            pop_size=4,
            generations=2,
            max_new=min(16, int(c["max_new_eval"])),
            eval_max_new=int(c["max_new_eval"]),
            lam=MIN_LAM,
        )
        row = {
            "family": "H-JOINT",
            "label": f"HJOINT_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "search_fit": float(meta["best_fit"]),
            "n_prompts": 2,
            "seed": seed,
            "best_gene": meta["best_gene"],
            "ckpt_source": "JOINT_bank",
            "lam": MIN_LAM,
        }
        write_json(out / f"HJOINT_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "joint_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "joint_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
