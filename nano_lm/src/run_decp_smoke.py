"""Smoke H-DECP on B2 ckpts; compare bank vs GLOBAL and B4."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_decp import run_h_decp
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
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        meta = run_h_decp(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=4,
            generations=2,
            max_new=min(16, int(c["max_new_eval"])),
            eval_max_new=int(c["max_new_eval"]),
            seed=seed,
            out_meta=out / f"HDECP_seed{seed}_train.json",
        )
        rows.append(
            {
                "family": "H-DECP",
                "label": f"HDECP_seed{seed}",
                "teacher_mean_logprob": float(meta["eval_fit"]),
                "mean_wall_ms": float(meta["eval_wall_ms"]),
                "search_fit": float(meta["best_fit"]),
                "n_prompts": 2,
                "seed": seed,
                "bank_n": len(meta["bank"]),
                "picks": meta["picks"],
            }
        )
        rows.append(
            {
                "family": "GLOBAL",
                "label": f"GLOBAL_seed{seed}",
                "teacher_mean_logprob": float(meta["global_eval_fit"]),
                "mean_wall_ms": float(meta["global_eval_wall_ms"]),
                "search_fit": float(meta["global_fit"]),
                "n_prompts": 2,
                "seed": seed,
                "best_gene": meta["global_gene"],
            }
        )
        write_json(out / f"HDECP_seed{seed}_eval.json", rows[-2])
    wall_s = time.perf_counter() - t0
    write_json(out / "decp_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "decp_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
