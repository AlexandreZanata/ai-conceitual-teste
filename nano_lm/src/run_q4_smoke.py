"""Smoke H-Q4: CUDA int4 weight-only decode on DEPTH_prun ckpt vs fp."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from q4_fit import DEFAULT_GROUP, DEFAULT_TILES, score_pair


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-Q4 requires CUDA", file=sys.stderr)
        return 2
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    prompts = _prompts(c["prompts"])
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        ckpt = out / f"HDEPTH_prun_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing DEPTH_prun ckpt: {ckpt}")
        early = _early_gene(out, seed)
        depth_row, q4_row = score_pair(
            early,
            ckpt=ckpt,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            claim=seed + 4040,
        )
        write_json(out / f"HQ4_seed{seed}_eval.json", q4_row)
        rows.extend([depth_row, q4_row])
    write_json(
        out / "q4_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "groupsize": DEFAULT_GROUP,
            "tiles": DEFAULT_TILES,
            "backend": "aten_int4pack_cuda",
            "ckpt": "HDEPTH_prun",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "q4_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
