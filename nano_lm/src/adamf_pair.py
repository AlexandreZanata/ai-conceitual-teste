"""Shared H-HALF vs H-ADAMF seed pair (eager AdamW vs fused)."""

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
    label_prefix: str = "HADAMF",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches and one top-k cache
    WHEN training HALF (eager AdamW) vs ADAMF (fused AdamW)
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
    half = train_topk_prefetch(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_half_seed{seed}.pt",
        hypothesis="H-HALF",
        half_h2d=True,
        fused_adam=False,
    )
    adamf = train_topk_prefetch(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}.pt",
        hypothesis="H-ADAMF",
        half_h2d=True,
        fused_adam=True,
    )
    half["cache_build_s"] = cache_meta["cache_build_s"]
    adamf["cache_build_s"] = cache_meta["cache_build_s"]
    write_json(out / f"{label_prefix}_half_seed{seed}_train.json", half)
    write_json(out / f"{label_prefix}_seed{seed}_train.json", adamf)
    ev_h = eval_ckpt(c, Path(half["out_path"]), seed, "H-HALF")
    ev_a = eval_ckpt(c, Path(adamf["out_path"]), seed, "H-ADAMF")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        row_htop(
            "H-HALF",
            f"{label_prefix}_half_seed{seed}",
            ev_h["teacher_mean_logprob"],
            half["ms_per_step"],
            half["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
        row_htop(
            "H-ADAMF",
            f"{label_prefix}_seed{seed}",
            ev_a["teacher_mean_logprob"],
            adamf["ms_per_step"],
            adamf["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
    ]
