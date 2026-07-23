"""Smoke H-POOL: cold H-DECKL pool then leave-one-out warm-start."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from hyp_deckl import run_h_deckl
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json

TOP_K = 1
LAM = 0.15


def _row(family: str, seed: int, meta: dict[str, Any]) -> dict[str, Any]:
    return {
        "family": family,
        "label": f"{family.replace('-', '')}_seed{seed}",
        "teacher_mean_logprob": float(meta["eval_fit"]),
        "mean_wall_ms": float(meta["eval_wall_ms"]),
        "search_fit": float(meta["best_fit"]),
        "n_prompts": 2,
        "seed": seed,
        "best_gene": meta["best_gene"],
        "teacher_forwards": int(meta["teacher_forwards"]),
        "wall_save": bool(meta["wall_save"]),
        "warm_start": bool(meta.get("warm_start")),
        "lam": LAM,
        "top_k": TOP_K,
    }


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    cold_genes: dict[int, dict] = {}
    t0 = time.perf_counter()
    max_new = min(16, int(c["max_new_eval"]))
    common = dict(
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["prompts"],
        cache_dir=c["cache"],
        pop_size=4,
        generations=2,
        max_new=max_new,
        eval_max_new=int(c["max_new_eval"]),
        top_k=TOP_K,
        lam=LAM,
    )
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        meta = run_h_deckl(
            student_ckpt=ckpt,
            seed=seed,
            out_meta=out / f"HDECKL_pool_cold_seed{seed}_train.json",
            **common,
        )
        cold_genes[seed] = meta["best_gene"]
        row = _row("H-DECKL", seed, meta)
        write_json(out / f"HDECKL_pool_cold_seed{seed}_eval.json", row)
        rows.append(row)
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        pool = [cold_genes[s] for s in c["seeds"] if s != seed]
        meta = run_h_deckl(
            student_ckpt=ckpt,
            seed=seed + 50,
            init_genes=pool,
            hypothesis="H-POOL",
            out_meta=out / f"HPOOL_seed{seed}_train.json",
            **common,
        )
        row = _row("H-POOL", seed, meta)
        write_json(out / f"HPOOL_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "pool_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "pool_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
