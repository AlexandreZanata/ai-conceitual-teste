"""Shared H-TOPK k-sweep seed runner (smoke)."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from load_model import load_causal_lm
from matrix_common import eval_ckpt, write_json
from stag_batch_plan import plan_cur_batches
from stag_ops import STAG_SEQ_LO
from top_cache import build_topk_cache, load_topk_cache
from top_pair import TIP_STAGES, row_htop
from top_train import train_topk_cache
from topk_ops import TOPK_SWEEP, slice_topk_records

__all__ = ["run_seed_ks", "run_seed_sweep"]


def run_seed_sweep(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    label_prefix: str = "HTOPK",
) -> list[dict[str, Any]]:
    """Smoke: full TOPK_SWEEP."""
    return run_seed_ks(
        c,
        out,
        seed,
        device,
        vocab,
        steps,
        ks=TOPK_SWEEP,
        label_prefix=label_prefix,
    )


def run_seed_ks(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    ks: tuple[int, ...],
    label_prefix: str = "HTOPK",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches and one max-k teacher cache
    WHEN training each k in ks at equal steps
    THEN return eval rows keyed by top_k (tip = 64).
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
    max_k = max(ks)
    cache_path = out / f"{label_prefix}_seed{seed}_cache_k{max_k}.pt"
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    cache_meta = build_topk_cache(
        teacher=teacher,
        batches=batches,
        out_path=cache_path,
        top_k=max_k,
    )
    write_json(out / f"{label_prefix}_seed{seed}_cache.json", cache_meta)
    del teacher
    if device.type == "cuda":
        torch.cuda.empty_cache()
    records_full, _stored = load_topk_cache(cache_path)
    rows: list[dict[str, Any]] = []
    for k in ks:
        rows.append(
            _train_eval_k(
                c,
                out,
                seed,
                device,
                vocab,
                k,
                slice_topk_records(records_full, k),
                float(cache_meta["cache_build_s"]),
                label_prefix=label_prefix,
            )
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return rows


def _train_eval_k(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    k: int,
    records: list[dict[str, torch.Tensor]],
    cache_build_s: float,
    *,
    label_prefix: str,
) -> dict[str, Any]:
    train = train_topk_cache(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}_k{k}.pt",
    )
    train["top_k"] = int(k)
    train["cache_build_s"] = cache_build_s
    write_json(out / f"{label_prefix}_seed{seed}_k{k}_train.json", train)
    ev = eval_ckpt(c, Path(train["out_path"]), seed, "H-TOPK")
    return row_htop(
        "H-TOPK",
        f"{label_prefix}_seed{seed}_k{k}",
        ev["teacher_mean_logprob"],
        train["ms_per_step"],
        train["train_wall_s"],
        seed,
        cache_build_s=cache_build_s,
        top_k=int(k),
    )
