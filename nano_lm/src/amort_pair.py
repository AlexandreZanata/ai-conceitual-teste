"""Train spine for H-AMORT: one cache, N PRE3 runs vs one live STAG."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from load_model import load_causal_lm
from matrix_common import eval_ckpt, write_json
from pre_train import train_topk_prefetch
from stag_batch_plan import plan_cur_batches
from stag_ops import STAG_SEQ_LO
from top_cache import build_topk_cache, load_topk_cache
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES
from top_train import train_live_batches

__all__ = ["run_amort_seed", "DEFAULT_TOP_K"]


def run_amort_seed(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    n_runs: int,
    *,
    label_prefix: str = "HAMORT",
) -> dict[str, Any]:
    """
    GIVEN shared STAG batches
    WHEN building cache once and training N PRE3 students + 1 live
    THEN return walls, lps, and cache_build_s for decide_hamort.
    """
    if int(n_runs) < 1:
        raise ValueError("n_runs must be >= 1")
    batches = plan_cur_batches(
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        steps=steps,
        batch_size=c["batch_size"],
        seq_len=c["seq_len"],
        max_examples=c["max_examples"],
        seq_lo=STAG_SEQ_LO,
        n_stages=TIP_STAGES,
        seed=seed + 101,
    )
    cache_path = out / f"{label_prefix}_seed{seed}_cache.pt"
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    live = train_live_batches(
        teacher=teacher,
        batches=batches,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_live_seed{seed}.pt",
    )
    write_json(out / f"{label_prefix}_live_seed{seed}_train.json", live)
    cache_meta = build_topk_cache(
        teacher=teacher,
        batches=batches,
        out_path=cache_path,
        top_k=DEFAULT_TOP_K,
    )
    write_json(out / f"{label_prefix}_seed{seed}_cache.json", cache_meta)
    del teacher
    if device.type == "cuda":
        torch.cuda.empty_cache()
    records, _k = load_topk_cache(cache_path)
    pre3_walls: list[float] = []
    pre3_lps: list[float] = []
    pre3_ms: list[float] = []
    for run in range(int(n_runs)):
        run_seed = seed + 101 + run
        tpack = train_topk_prefetch(
            records=records,
            vocab_size=vocab,
            device=device,
            lr=c["lr"],
            seed=run_seed,
            temperature=2.0,
            alpha=0.5,
            out_path=out / f"{label_prefix}_seed{seed}_run{run}.pt",
            hypothesis="H-AMORT",
            half_h2d=True,
            fused_adam=True,
            prefetch_depth=3,
        )
        write_json(out / f"{label_prefix}_seed{seed}_run{run}_train.json", tpack)
        ev = eval_ckpt(c, Path(tpack["out_path"]), seed, "H-AMORT")
        pre3_walls.append(float(tpack["train_wall_s"]))
        pre3_lps.append(float(ev["teacher_mean_logprob"]))
        pre3_ms.append(float(tpack["ms_per_step"]))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    ev_live = eval_ckpt(c, Path(live["out_path"]), seed, "H-STAG")
    return {
        "seed": seed,
        "live_lp": float(ev_live["teacher_mean_logprob"]),
        "live_train_wall_s": float(live["train_wall_s"]),
        "live_ms_step": float(live["ms_per_step"]),
        "cache_build_s": float(cache_meta["cache_build_s"]),
        "pre3_train_walls": pre3_walls,
        "pre3_lps": pre3_lps,
        "pre3_ms_steps": pre3_ms,
        "n_runs": int(n_runs),
    }
