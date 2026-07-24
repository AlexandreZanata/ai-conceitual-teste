"""Smoke H-POOL2: tighter pop×gens + elite warm-start vs H-POOL tip."""

from __future__ import annotations

import json
import random
import sys
import time
from pathlib import Path
from typing import Any

from hyp_deckl import run_h_deckl
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from pool2_ops import POOL2_GENS, POOL2_POP, warm_start_pop2

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
        "wall_save": bool(meta.get("wall_save")),
        "warm_start": bool(meta.get("warm_start")),
        "lam": LAM,
        "top_k": TOP_K,
        "pop_size": int(meta.get("pop_size", 0)),
        "generations": int(meta.get("generations", 0)),
    }


def _cold_gene(out: Path, seed: int) -> dict:
    path = out / f"HDECKL_pool_cold_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing cold DECKL tip: {path}")
    return json.loads(path.read_text(encoding="utf-8"))["best_gene"]


def _pool_tip_row(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HPOOL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing H-POOL tip: {path}")
    row = json.loads(path.read_text(encoding="utf-8"))
    row["family"] = "H-POOL"
    train = out / f"HPOOL_seed{seed}_train.json"
    if train.is_file():
        meta = json.loads(train.read_text(encoding="utf-8"))
        row["teacher_forwards"] = int(meta.get("teacher_forwards", row.get("teacher_forwards", 0)))
    return row


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
    for seed in c["seeds"]:
        cold_genes[seed] = _cold_gene(out, seed)
        rows.append(_pool_tip_row(out, seed))
    for seed in c["seeds"]:
        ckpt = out / f"B2_seed{seed}.pt"
        if not ckpt.is_file():
            raise FileNotFoundError(f"missing B2 checkpoint: {ckpt}")
        pool = [cold_genes[s] for s in c["seeds"] if s != seed]
        rng = random.Random(seed + 90)
        init = warm_start_pop2(pool, POOL2_POP, rng)
        meta = run_h_deckl(
            student_ckpt=ckpt,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=POOL2_POP,
            generations=POOL2_GENS,
            max_new=max_new,
            eval_max_new=int(c["max_new_eval"]),
            seed=seed + 90,
            init_genes=init,
            hypothesis="H-POOL2",
            out_meta=out / f"HPOOL2_seed{seed}_train.json",
            top_k=TOP_K,
            lam=LAM,
        )
        meta["pop_size"] = POOL2_POP
        meta["generations"] = POOL2_GENS
        row = _row("H-POOL2", seed, meta)
        write_json(out / f"HPOOL2_seed{seed}_eval.json", row)
        rows.append(row)
    wall_s = time.perf_counter() - t0
    write_json(out / "pool2_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "pool2_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
