"""Smoke H-DECQ vs same-run H-DECM and matrix B4."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from decm_ops import MIX_M
from hyp_decm import run_h_decm
from hyp_decq import run_h_decq
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
        common = dict(
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
        )
        decm = run_h_decm(**common, out_meta=out / f"HDECM_qctrl_seed{seed}.json")
        rows.append(
            {
                "family": "H-DECM",
                "label": f"HDECM_qctrl_seed{seed}",
                "teacher_mean_logprob": float(decm["eval_fit"]),
                "mean_wall_ms": float(decm["eval_wall_ms"]),
                "n_prompts": 2,
                "seed": seed,
            }
        )
        decq = run_h_decq(**common, out_meta=out / f"HDECQ_seed{seed}_train.json")
        rows.append(
            {
                "family": "H-DECQ",
                "label": f"HDECQ_seed{seed}",
                "teacher_mean_logprob": float(decq["eval_fit"]),
                "mean_wall_ms": float(decq["eval_wall_ms"]),
                "search_fit": float(decq["best_fit"]),
                "n_prompts": 2,
                "seed": seed,
                "mix_m": MIX_M,
                "picks": decq["picks"],
            }
        )
        write_json(out / f"HDECQ_seed{seed}_eval.json", rows[-1])
    wall_s = time.perf_counter() - t0
    write_json(out / "decq_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "decq_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
