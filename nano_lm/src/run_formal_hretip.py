"""Formal H-RETIP: PRE3 vs live STAG + frozen EARLY/POOL (fit≠eval)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from data_tiny import load_tokenizer
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from retip_ops import decide_hretip
from retip_score import load_best_gene, serve_pair
from run_formal_htpack import formal_cfg as htpack_formal_cfg
from stag_ops import STAG_SEQ_LO
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES
from tpack_pair import eval_seed_rows, train_seed_pair


def formal_cfg() -> dict[str, Any]:
    base = htpack_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hretip"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["pool_dir"] = REPO / "results/nano-lm/formal-hpool"
    return base


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def _means(vals: list[float]) -> float:
    return sum(vals) / max(len(vals), 1)


def _mean_map(rows: list[dict[str, float]]) -> dict[str, float]:
    return {
        "mean_lp": _means([float(r["mean_lp"]) for r in rows]),
        "mean_wall": _means([float(r["mean_wall"]) for r in rows]),
    }


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-RETIP formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    early_dir = Path(c["early_dir"])
    pool_dir = Path(c["pool_dir"])
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    vocab = len(tok)
    steps = int(c["steps_kd"])
    prompts = _texts(c["prompts"])
    max_new = int(c.get("max_new_eval", 48))
    t0 = time.perf_counter()
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
            c, out, seed, device, vocab, steps, label_prefix="HRETIP_formal"
        )
        ar = eval_seed_rows(
            c, live, tpack, seed, label_prefix="HRETIP_formal"
        )
        live_lp = float(ar[0]["teacher_mean_logprob"])
        retip_lp = float(ar[1]["teacher_mean_logprob"])
        ar_live.append(live_lp)
        ar_retip.append(retip_lp)
        early_gene = load_best_gene(early_dir / f"HEARLY_seed{seed}_train.json")
        pool_gene = load_best_gene(pool_dir / f"HPOOL_seed{seed}_train.json")
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
            seed=seed + 8000,
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
        torch.cuda.empty_cache()
    control_lp = _means(ar_live)
    retip_lp = _means(ar_retip)
    early_c = _mean_map(early_c_rows)
    early_r = _mean_map(early_r_rows)
    pool_c = _mean_map(pool_c_rows)
    pool_r = _mean_map(pool_r_rows)
    decision = decide_hretip(
        retip_lp=retip_lp,
        control_lp=control_lp,
        early_retip=early_r,
        early_control=early_c,
        pool_retip=pool_r,
        pool_control=pool_c,
    )
    write_json(
        out / "formal.json",
        {
            "seed_rows": seed_rows,
            "mean_ar_live": control_lp,
            "mean_ar_retip": retip_lp,
            "early_control": early_c,
            "early_retip": early_r,
            "pool_control": pool_c,
            "pool_retip": pool_r,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k": DEFAULT_TOP_K,
            "max_new": max_new,
            "n_prompts": len(prompts),
            "mode": "PRE3 retip vs live STAG; frozen EARLY/POOL serve",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
