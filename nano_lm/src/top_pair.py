"""Shared live-STAG vs H-TOP seed pair (smoke + formal)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from load_model import load_causal_lm
from matrix_common import eval_ckpt, write_json
from stag_batch_plan import plan_cur_batches
from stag_ops import STAG_SEQ_LO
from top_cache import build_topk_cache, load_topk_cache
from top_ops import DEFAULT_TOP_K
from top_train import train_live_batches, train_topk_cache

TIP_STAGES = 4


def row_htop(
    family: str,
    label: str,
    lp: float,
    ms_step: float,
    train_wall_s: float,
    seed: int,
    *,
    cache_build_s: float = 0.0,
    top_k: int = 0,
) -> dict[str, Any]:
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(lp),
        "mean_ms_step": float(ms_step),
        "train_wall_s": float(train_wall_s),
        "cache_build_s": float(cache_build_s),
        "top_k": int(top_k),
        "seed": seed,
    }


def run_seed_pair(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    label_prefix: str = "HTOP",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches
    WHEN training live KD vs top-k cache
    THEN return eval rows for H-STAG control and H-TOP.
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
    del teacher
    if device.type == "cuda":
        torch.cuda.empty_cache()
    records, _k = load_topk_cache(cache_path)
    top = train_topk_cache(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}.pt",
    )
    top["cache_build_s"] = cache_meta["cache_build_s"]
    top["top_k"] = DEFAULT_TOP_K
    write_json(out / f"{label_prefix}_seed{seed}_train.json", top)
    ev_l = eval_ckpt(c, Path(live["out_path"]), seed, "H-STAG")
    ev_t = eval_ckpt(c, Path(top["out_path"]), seed, "H-TOP")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        row_htop(
            "H-STAG",
            f"{label_prefix}_live_seed{seed}",
            ev_l["teacher_mean_logprob"],
            live["ms_per_step"],
            live["train_wall_s"],
            seed,
        ),
        row_htop(
            "H-TOP",
            f"{label_prefix}_seed{seed}",
            ev_t["teacher_mean_logprob"],
            top["ms_per_step"],
            top["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
    ]
