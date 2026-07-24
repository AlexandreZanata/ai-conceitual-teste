"""Smoke H-FLOP: B3 AR vs H-EARLY with wall + tps + est GFLOPs."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from decode_ar import decode_ar
from decode_early import decode_early
from eval_decode import load_pair
from flop_score import load_prompts, score_with_flops
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip gene: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _score_seed(c: dict, out: Path, seed: int) -> list[dict[str, Any]]:
    ckpt = out / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    prompts = load_prompts(c["prompts"])
    max_new = int(c["max_new_eval"])
    gene = _early_gene(out, seed)
    shared = dict(
        teacher=teacher,
        student=student,
        prompts=prompts,
        seed=seed,
        max_new_tokens=max_new,
    )
    ar = score_with_flops(
        family="B3",
        label=f"B3_seed{seed}",
        decode_fn=decode_ar,
        decode_kwargs={"temperature": 0.8, "top_p": 0.9},
        **shared,
    )
    early = score_with_flops(
        family="H-EARLY",
        label=f"HEARLY_flop_seed{seed}",
        decode_fn=decode_early,
        decode_kwargs={
            "n": int(gene["n"]),
            "min_new": int(gene["min_new"]),
            "conf_threshold": float(gene["conf_threshold"]),
            "patience": int(gene["patience"]),
            "temperature": float(gene["temperature"]),
            "top_p": float(gene["top_p"]),
        },
        **shared,
    )
    return [ar, early]


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
        for row in _score_seed(c, out, seed):
            write_json(out / f"{row['label']}_flop_eval.json", row)
            rows.append(row)
    write_json(
        out / "flop_smoke.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "flop_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
