"""Shared H-TIPD measurement loop (train PRE3 vs live + frozen serve)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
import yaml

from retip_score import load_best_gene, serve_pair
from tipd_ops import decide_htipd, tip_outcome
from tpack_pair import eval_seed_rows, train_seed_pair

__all__ = [
    "load_texts",
    "means",
    "mean_map",
    "run_tipd_seeds",
    "tune_cpu_threads",
]


def tune_cpu_threads(n: int | None = None) -> int:
    """
    GIVEN host CPU count
    WHEN preparing TIPD train/eval
    THEN pin torch/OMP threads high but leave ≥4 cores free.
    """
    import os

    cpus = int(os.cpu_count() or 4)
    use = int(n) if n is not None else max(4, cpus - 4)
    use = min(use, cpus)
    os.environ.setdefault("OMP_NUM_THREADS", str(use))
    os.environ.setdefault("MKL_NUM_THREADS", str(use))
    torch.set_num_threads(use)
    return use


def load_texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def means(vals: list[float]) -> float:
    return sum(vals) / max(len(vals), 1)


def mean_map(rows: list[dict[str, float]]) -> dict[str, float]:
    return {
        "mean_lp": means([float(r["mean_lp"]) for r in rows]),
        "mean_wall": means([float(r["mean_wall"]) for r in rows]),
    }


def run_tipd_seeds(
    c: dict[str, Any],
    *,
    out: Path,
    device,
    vocab: int,
    steps: int,
    prompts: list[str],
    max_new: int,
    early_dir: Path,
    pool_dir: Path,
    label_prefix: str,
    claim_base: int,
    pool_eval_fallback: bool = True,
) -> dict[str, Any]:
    """
    GIVEN matrix cfg + tip gene dirs
    WHEN training live vs PRE3 and scoring frozen EARLY/POOL
    THEN return means + decide_htipd payload fields.
    """
    ar_live: list[float] = []
    ar_retip: list[float] = []
    early_c_rows: list[dict[str, float]] = []
    early_r_rows: list[dict[str, float]] = []
    pool_c_rows: list[dict[str, float]] = []
    pool_r_rows: list[dict[str, float]] = []
    seed_rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "train", "seed": seed}), flush=True)
        live, tpack = train_seed_pair(
            c, out, seed, device, vocab, steps, label_prefix=label_prefix
        )
        ar = eval_seed_rows(c, live, tpack, seed, label_prefix=label_prefix)
        live_lp = float(ar[0]["teacher_mean_logprob"])
        retip_lp = float(ar[1]["teacher_mean_logprob"])
        ar_live.append(live_lp)
        ar_retip.append(retip_lp)
        early_gene = load_best_gene(early_dir / f"HEARLY_seed{seed}_train.json")
        pool_path = pool_dir / f"HPOOL_seed{seed}_eval.json"
        if pool_eval_fallback and not pool_path.is_file():
            pool_path = pool_dir / f"HPOOL_seed{seed}_train.json"
        elif not pool_eval_fallback:
            pool_path = pool_dir / f"HPOOL_seed{seed}_train.json"
        pool_gene = load_best_gene(pool_path)
        print(json.dumps({"phase": "serve", "seed": seed}), flush=True)
        scored = serve_pair(
            live_ckpt=Path(live["out_path"]),
            retip_ckpt=Path(tpack["out_path"]),
            early_gene=early_gene,
            pool_gene=pool_gene,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            prompts=prompts,
            max_new=max_new,
            seed=seed + claim_base,
        )
        early_c_rows.append(scored["early_control"])
        early_r_rows.append(scored["early_retip"])
        pool_c_rows.append(scored["pool_control"])
        pool_r_rows.append(scored["pool_retip"])
        seed_rows.append(
            {
                "seed": seed,
                "ar_live": live_lp,
                "ar_retip": retip_lp,
                "ms_live": float(live["ms_per_step"]),
                "ms_retip": float(tpack["ms_per_step"]),
                **{f"s_{k}": v for k, v in scored.items()},
            }
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    control_lp = means(ar_live)
    retip_lp = means(ar_retip)
    early_c = mean_map(early_c_rows)
    early_r = mean_map(early_r_rows)
    pool_c = mean_map(pool_c_rows)
    pool_r = mean_map(pool_r_rows)
    decision = decide_htipd(
        retip_lp=retip_lp,
        control_lp=control_lp,
        early_retip=early_r,
        early_control=early_c,
        pool_retip=pool_r,
        pool_control=pool_c,
    )
    return {
        "seed_rows": seed_rows,
        "mean_ar_live": control_lp,
        "mean_ar_retip": retip_lp,
        "early_control": early_c,
        "early_retip": early_r,
        "pool_control": pool_c,
        "pool_retip": pool_r,
        "decision": decision,
        "tip_outcome": tip_outcome(decision),
    }
