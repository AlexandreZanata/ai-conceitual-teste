"""Smoke H-MNG: stack tip metas; dual gate vs H-MINP + H-NGRAM."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_mng import run_h_mng
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
        minp_train = out / f"HMINP_seed{seed}_train.json"
        ngram_train = out / f"HNGRAM_seed{seed}_train.json"
        for p in (ckpt, minp_train, ngram_train):
            if not p.is_file():
                raise FileNotFoundError(f"missing tip artifact: {p}")
        meta = run_h_mng(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            max_new=int(c["max_new_eval"]),
            seed=seed,
            minp_train=minp_train,
            ngram_train=ngram_train,
            out_meta=out / f"HMNG_seed{seed}_train.json",
        )
        row = {
            "family": "H-MNG",
            "label": f"HMNG_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "min_p": float(meta["min_p"]),
            "ngram_size": int(meta["ngram_size"]),
            "n_prompts": 2,
            "seed": seed,
        }
        write_json(out / f"HMNG_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "mng_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "mng_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
