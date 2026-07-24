"""Smoke H-SYS: CURL lo=8 ckpt × EARLY|POOL decode arms."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from hyp_deckl import run_h_deckl
from hyp_early import run_h_early
from lat2_ops import MIN_LAM
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from sys_ops import SYS_EARLY, SYS_POOL


def _meta_row(family: str, seed: int, meta: dict[str, Any], **extra: Any) -> dict:
    row = {
        "family": family,
        "label": f"{family.replace('-', '')}_seed{seed}",
        "teacher_mean_logprob": float(meta["eval_fit"]),
        "mean_wall_ms": float(meta["eval_wall_ms"]),
        "search_fit": float(meta["best_fit"]),
        "n_prompts": 2,
        "seed": seed,
        "best_gene": meta["best_gene"],
        "ckpt_source": "CURL_lo8",
    }
    row.update(extra)
    return row


def _load_cold_genes(out: Path, seeds: list[int]) -> dict[int, dict]:
    genes: dict[int, dict] = {}
    for seed in seeds:
        path = out / f"HDECKL_pool_cold_seed{seed}_train.json"
        if not path.is_file():
            raise FileNotFoundError(f"missing cold DECKL gene: {path}")
        genes[seed] = json.loads(path.read_text(encoding="utf-8"))["best_gene"]
    return genes


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    cold = _load_cold_genes(out, list(c["seeds"]))
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    max_new = min(16, int(c["max_new_eval"]))
    for seed in c["seeds"]:
        curl = out / f"HCURL_lo8_seed{seed}.pt"
        if not curl.is_file():
            raise FileNotFoundError(f"missing CURL lo=8 ckpt: {curl}")
        early = run_h_early(
            student_ckpt=curl,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=4,
            generations=2,
            max_new=max_new,
            eval_max_new=int(c["max_new_eval"]),
            seed=seed + 200,
            lam=MIN_LAM,
            out_meta=out / f"HSYSE_seed{seed}_train.json",
        )
        er = _meta_row(SYS_EARLY, seed, early, decode_arm="EARLY", lam=MIN_LAM)
        write_json(out / f"HSYSE_seed{seed}_eval.json", er)
        rows.append(er)
        if device.type == "cuda":
            torch.cuda.empty_cache()
        pool = [cold[s] for s in c["seeds"] if s != seed]
        pool_meta = run_h_deckl(
            student_ckpt=curl,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=4,
            generations=2,
            max_new=max_new,
            eval_max_new=int(c["max_new_eval"]),
            seed=seed + 250,
            top_k=1,
            lam=0.15,
            init_genes=pool,
            hypothesis="H-SYS-P",
            out_meta=out / f"HSYSP_seed{seed}_train.json",
        )
        pr = _meta_row(
            SYS_POOL,
            seed,
            pool_meta,
            decode_arm="POOL",
            lam=0.15,
            top_k=1,
            warm_start=True,
        )
        write_json(out / f"HSYSP_seed{seed}_eval.json", pr)
        rows.append(pr)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    wall_s = time.perf_counter() - t0
    write_json(out / "sys_smoke.json", {"rows": rows, "wall_s": wall_s})
    print(json.dumps({"n_rows": len(rows), "out": str(out / "sys_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
