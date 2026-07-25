"""Shared H-PRE2 vs H-PRE3 seed pair (2-deep vs 3-deep prefetch)."""

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
from top_pair import TIP_STAGES, row_htop

__all__ = ["run_seed_pair"]


def run_seed_pair(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    label_prefix: str = "HPRE3",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches and one top-k cache
    WHEN training PRE2 (depth=2) vs PRE3 (depth=3) under ADAMF I/O
    THEN return eval rows for both (equal steps).
    """
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
    pre2 = train_topk_prefetch(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_pre2_seed{seed}.pt",
        hypothesis="H-PRE2",
        half_h2d=True,
        fused_adam=True,
        prefetch_depth=2,
    )
    pre3 = train_topk_prefetch(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}.pt",
        hypothesis="H-PRE3",
        half_h2d=True,
        fused_adam=True,
        prefetch_depth=3,
    )
    pre2["cache_build_s"] = cache_meta["cache_build_s"]
    pre3["cache_build_s"] = cache_meta["cache_build_s"]
    write_json(out / f"{label_prefix}_pre2_seed{seed}_train.json", pre2)
    write_json(out / f"{label_prefix}_seed{seed}_train.json", pre3)
    ev_2 = eval_ckpt(c, Path(pre2["out_path"]), seed, "H-PRE2")
    ev_3 = eval_ckpt(c, Path(pre3["out_path"]), seed, "H-PRE3")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        row_htop(
            "H-PRE2",
            f"{label_prefix}_pre2_seed{seed}",
            ev_2["teacher_mean_logprob"],
            pre2["ms_per_step"],
            pre2["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
        row_htop(
            "H-PRE3",
            f"{label_prefix}_seed{seed}",
            ev_3["teacher_mean_logprob"],
            pre3["ms_per_step"],
            pre3["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
    ]
