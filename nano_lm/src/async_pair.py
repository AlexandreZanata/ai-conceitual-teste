"""Shared H-PIN sequential vs H-ASYNC pipelined seed pair."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from async_ops import e2e_wall_s
from async_train import train_async_pin
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
    label_prefix: str = "HASYNC",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches
    WHEN comparing async pipeline vs sequential PIN
    THEN return eval rows with e2e_wall_s for both.
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
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    # Async first (cold GPU): overlap build(i+1) with PIN train(i).
    async_row = train_async_pin(
        teacher=teacher,
        batches=batches,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}.pt",
        top_k=DEFAULT_TOP_K,
    )
    write_json(out / f"{label_prefix}_seed{seed}_train.json", async_row)
    # Sequential PIN: full cache then pinned train.
    cache_path = out / f"{label_prefix}_seed{seed}_cache.pt"
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
    pin = train_topk_cache(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_pin_seed{seed}.pt",
        pinned=True,
        hypothesis="H-PIN",
    )
    pin_e2e = e2e_wall_s(
        cache_build_s=float(cache_meta["cache_build_s"]),
        train_wall_s=float(pin["train_wall_s"]),
    )
    pin["e2e_wall_s"] = pin_e2e
    pin["cache_build_s"] = cache_meta["cache_build_s"]
    write_json(out / f"{label_prefix}_pin_seed{seed}_train.json", pin)
    ev_a = eval_ckpt(c, Path(async_row["out_path"]), seed, "H-ASYNC")
    ev_p = eval_ckpt(c, Path(pin["out_path"]), seed, "H-PIN")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        _row(
            "H-PIN",
            f"{label_prefix}_pin_seed{seed}",
            ev_p["teacher_mean_logprob"],
            pin["ms_per_step"],
            pin["train_wall_s"],
            seed,
            e2e_wall_s=pin_e2e,
            cache_build_s=float(cache_meta["cache_build_s"]),
        ),
        _row(
            "H-ASYNC",
            f"{label_prefix}_seed{seed}",
            ev_a["teacher_mean_logprob"],
            async_row["ms_per_step"],
            async_row["train_wall_s"],
            seed,
            e2e_wall_s=float(async_row["e2e_wall_s"]),
            cache_build_s=0.0,
        ),
    ]


def _row(
    family: str,
    label: str,
    lp: float,
    ms_step: float,
    train_wall_s: float,
    seed: int,
    *,
    e2e_wall_s: float,
    cache_build_s: float,
) -> dict[str, Any]:
    r = row_htop(
        family,
        label,
        lp,
        ms_step,
        train_wall_s,
        seed,
        cache_build_s=cache_build_s,
        top_k=DEFAULT_TOP_K,
    )
    r["e2e_wall_s"] = float(e2e_wall_s)
    return r
