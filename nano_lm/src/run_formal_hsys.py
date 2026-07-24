"""Formal-budget H-SYS: CURL lo=8 × EARLY|POOL; fit≠eval."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_deckl import run_h_deckl
from hyp_early import run_h_early
from lat2_ops import MIN_LAM
from load_model import resolve_device
from matrix_common import REPO, eval_ckpt, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg
from sys_ops import SYS_EARLY, SYS_POOL


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hsys"
    base["curl_dir"] = REPO / "results/nano-lm/formal-hcurl"
    base["b2_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    return base


def _row(family: str, seed: int, meta: dict[str, Any], **extra: Any) -> dict:
    row = {
        "family": family,
        "label": f"{family.replace('-', '')}_seed{seed}",
        "teacher_mean_logprob": float(meta["eval_fit"]),
        "mean_wall_ms": float(meta["eval_wall_ms"]),
        "best_gene": meta["best_gene"],
        "seed": seed,
        "ckpt_source": extra.pop("ckpt_source", "CURL_lo8"),
    }
    row.update(extra)
    attach_overfit(row, float(meta["best_fit"]))
    return row


def _common_dec(c: dict[str, Any]) -> dict[str, Any]:
    return dict(
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["fit_prompts"],
        cache_dir=c["cache"],
        pop_size=c["dec_pop"],
        generations=c["dec_gens"],
        max_new=c["max_new_fit"],
        eval_max_new=c["max_new_eval"],
        top_k=1,
        lam=0.15,
    )


def _seed_controls(
    c: dict[str, Any], device: torch.device, seed: int, cold: dict[int, dict]
) -> list[dict[str, Any]]:
    b2 = c["b2_dir"] / f"B2_seed{seed}.pt"
    curl = c["curl_dir"] / f"HCURL_lo8_seed{seed}.pt"
    if not b2.is_file() or not curl.is_file():
        raise FileNotFoundError(f"missing formal ckpt seed={seed}")
    rows = [eval_ckpt(c, curl, seed, "H-CURL")]
    early = run_h_early(
        student_ckpt=b2,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["fit_prompts"],
        eval_prompts_path=c["prompts"],
        cache_dir=c["cache"],
        pop_size=c["dec_pop"],
        generations=c["dec_gens"],
        max_new=c["max_new_fit"],
        eval_max_new=c["max_new_eval"],
        seed=seed,
        lam=MIN_LAM,
        out_meta=c["out"] / f"HEARLY_B2_seed{seed}_train.json",
    )
    rows.append(_row("H-EARLY", seed, early, ckpt_source="B2"))
    if device.type == "cuda":
        torch.cuda.empty_cache()
    cold_meta = run_h_deckl(
        student_ckpt=b2,
        seed=seed,
        out_meta=c["out"] / f"HDECKL_cold_seed{seed}_train.json",
        **_common_dec(c),
    )
    cold[seed] = cold_meta["best_gene"]
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return rows


def _seed_arms(
    c: dict[str, Any], device: torch.device, seed: int, cold: dict[int, dict]
) -> list[dict[str, Any]]:
    b2 = c["b2_dir"] / f"B2_seed{seed}.pt"
    curl = c["curl_dir"] / f"HCURL_lo8_seed{seed}.pt"
    pool = [cold[s] for s in c["seeds"] if s != seed]
    rows: list[dict[str, Any]] = []
    pool_b2 = run_h_deckl(
        student_ckpt=b2,
        seed=seed + 50,
        init_genes=pool,
        hypothesis="H-POOL",
        out_meta=c["out"] / f"HPOOL_B2_seed{seed}_train.json",
        **_common_dec(c),
    )
    rows.append(_row("H-POOL", seed, pool_b2, ckpt_source="B2", warm_start=True))
    if device.type == "cuda":
        torch.cuda.empty_cache()
    early_c = run_h_early(
        student_ckpt=curl,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["fit_prompts"],
        eval_prompts_path=c["prompts"],
        cache_dir=c["cache"],
        pop_size=c["dec_pop"],
        generations=c["dec_gens"],
        max_new=c["max_new_fit"],
        eval_max_new=c["max_new_eval"],
        seed=seed + 200,
        lam=MIN_LAM,
        out_meta=c["out"] / f"HSYSE_seed{seed}_train.json",
    )
    rows.append(_row(SYS_EARLY, seed, early_c, decode_arm="EARLY"))
    if device.type == "cuda":
        torch.cuda.empty_cache()
    pool_c = run_h_deckl(
        student_ckpt=curl,
        seed=seed + 250,
        init_genes=pool,
        hypothesis="H-SYS-P",
        out_meta=c["out"] / f"HSYSP_seed{seed}_train.json",
        **_common_dec(c),
    )
    rows.append(_row(SYS_POOL, seed, pool_c, decode_arm="POOL", warm_start=True))
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return rows


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    cold: dict[int, dict] = {}
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_seed_controls(c, device, seed, cold))
    for seed in c["seeds"]:
        rows.extend(_seed_arms(c, device, seed, cold))
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in c.items()},
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
