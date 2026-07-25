"""Shared live H-STAG vs H-ETRAIN (PRE3 e2e) seed pair."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import torch

from etrain_ops import e2e_wall_s
from load_model import load_causal_lm
from matrix_common import eval_ckpt, write_json
from pre_train import train_topk_prefetch
from stag_batch_plan import plan_cur_batches
from stag_ops import STAG_SEQ_LO
from top_cache import build_topk_cache, load_topk_cache
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES, row_htop
from top_train import train_live_batches

__all__ = ["run_seed_pair", "row_etrain"]


def row_etrain(
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
    row = row_htop(
        family,
        label,
        lp,
        ms_step,
        train_wall_s,
        seed,
        cache_build_s=cache_build_s,
        top_k=top_k,
    )
    row["e2e_wall_s"] = e2e_wall_s(
        cache_build_s=cache_build_s, train_wall_s=train_wall_s
    )
    return row


def run_seed_pair(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    label_prefix: str = "HETRAIN",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches
    WHEN training live STAG vs PRE3 stack (cache build + depth-3 train)
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
    etrain = train_topk_prefetch(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}.pt",
        hypothesis="H-ETRAIN",
        half_h2d=True,
        fused_adam=True,
        prefetch_depth=3,
    )
    etrain["cache_build_s"] = cache_meta["cache_build_s"]
    etrain["e2e_wall_s"] = e2e_wall_s(
        cache_build_s=float(cache_meta["cache_build_s"]),
        train_wall_s=float(etrain["train_wall_s"]),
    )
    write_json(out / f"{label_prefix}_seed{seed}_train.json", etrain)
    ev_l = eval_ckpt(c, Path(live["out_path"]), seed, "H-STAG")
    ev_e = eval_ckpt(c, Path(etrain["out_path"]), seed, "H-ETRAIN")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        row_etrain(
            "H-STAG",
            f"{label_prefix}_live_seed{seed}",
            ev_l["teacher_mean_logprob"],
            live["ms_per_step"],
            live["train_wall_s"],
            seed,
        ),
        row_etrain(
            "H-ETRAIN",
            f"{label_prefix}_seed{seed}",
            ev_e["teacher_mean_logprob"],
            etrain["ms_per_step"],
            etrain["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
    ]
