"""Shared H-TOP vs H-PIN seed pair (same cache; pageable vs pinned H2D)."""

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
from top_pair import TIP_STAGES, row_htop
from top_train import train_topk_cache

__all__ = ["run_seed_pair"]


def run_seed_pair(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    label_prefix: str = "HPIN",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches and one top-k cache
    WHEN training pageable H-TOP vs pinned H-PIN
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
    top = train_topk_cache(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_top_seed{seed}.pt",
        pinned=False,
        hypothesis="H-TOP",
    )
    pin = train_topk_cache(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}.pt",
        pinned=True,
        hypothesis="H-PIN",
    )
    top["cache_build_s"] = cache_meta["cache_build_s"]
    pin["cache_build_s"] = cache_meta["cache_build_s"]
    write_json(out / f"{label_prefix}_top_seed{seed}_train.json", top)
    write_json(out / f"{label_prefix}_seed{seed}_train.json", pin)
    ev_t = eval_ckpt(c, Path(top["out_path"]), seed, "H-TOP")
    ev_p = eval_ckpt(c, Path(pin["out_path"]), seed, "H-PIN")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        row_htop(
            "H-TOP",
            f"{label_prefix}_top_seed{seed}",
            ev_t["teacher_mean_logprob"],
            top["ms_per_step"],
            top["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
        row_htop(
            "H-PIN",
            f"{label_prefix}_seed{seed}",
            ev_p["teacher_mean_logprob"],
            pin["ms_per_step"],
            pin["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
    ]
