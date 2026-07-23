"""Smoke H-DECM on B2 ckpts; compare mixture vs H-LAT2 and B4."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from decm_ops import MIX_M
from hyp_decm import run_h_decm
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
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        meta = run_h_decm(
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
            lam=MIN_LAM,
            mix_m=MIX_M,
            out_meta=out / f"HDECM_seed{seed}_train.json",
        )
        rows.append(
            {
                "family": "H-DECM",
                "label": f"HDECM_seed{seed}",
                "teacher_mean_logprob": float(meta["eval_fit"]),
                "mean_wall_ms": float(meta["eval_wall_ms"]),
                "search_fit": float(meta["best_fit"]),
                "n_prompts": 2,
                "seed": seed,
                "mix_m": MIX_M,
                "picks": meta["picks"],
            }
        )
        rows.append(
            {
                "family": "H-LAT2",
                "label": f"HLAT2_ctrl_seed{seed}",
                "teacher_mean_logprob": float(meta["lat2_eval_fit"]),
                "mean_wall_ms": float(meta["lat2_eval_wall_ms"]),
                "n_prompts": 2,
                "seed": seed,
                "best_gene": meta["best_gene"],
            }
        )
        write_json(out / f"HDECM_seed{seed}_eval.json", rows[-2])
    wall_s = time.perf_counter() - t0
    write_json(out / "decm_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "decm_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
