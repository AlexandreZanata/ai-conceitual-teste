"""Shared live H-STAG vs H-TPACK (PRE3 ms/step) seed pair."""

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
from top_train import train_live_batches

__all__ = ["run_seed_pair", "train_seed_pair", "eval_seed_rows"]


def train_seed_pair(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    label_prefix: str = "HTPACK",
) -> tuple[dict[str, Any], dict[str, Any]]:
    """
    GIVEN shared STAG batches
    WHEN training live STAG vs PRE3 stack
    THEN return (live, tpack) train dicts with out_path / ms_per_step.
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
    tpack = train_topk_prefetch(
        records=records,
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"{label_prefix}_seed{seed}.pt",
        hypothesis="H-TPACK",
        half_h2d=True,
        fused_adam=True,
        prefetch_depth=3,
    )
    tpack["cache_build_s"] = cache_meta["cache_build_s"]
    write_json(out / f"{label_prefix}_seed{seed}_train.json", tpack)
    return live, tpack


def eval_seed_rows(
    c: dict[str, Any],
    live: dict[str, Any],
    tpack: dict[str, Any],
    seed: int,
    *,
    label_prefix: str = "HTPACK",
    prompts_path: Path | None = None,
    pack_tag: str = "",
) -> list[dict[str, Any]]:
    """Eval live STAG + TPACK on prompts_path (default c['prompts'])."""
    cfg = dict(c)
    if prompts_path is not None:
        cfg["prompts"] = prompts_path
    tag = f"_{pack_tag}" if pack_tag else ""
    ev_l = eval_ckpt(cfg, Path(live["out_path"]), seed, "H-STAG")
    ev_t = eval_ckpt(cfg, Path(tpack["out_path"]), seed, "H-TPACK")
    cache_s = float(tpack.get("cache_build_s", 0.0))
    return [
        row_htop(
            "H-STAG",
            f"{label_prefix}_live{tag}_seed{seed}",
            ev_l["teacher_mean_logprob"],
            live["ms_per_step"],
            live["train_wall_s"],
            seed,
        ),
        row_htop(
            "H-TPACK",
            f"{label_prefix}{tag}_seed{seed}",
            ev_t["teacher_mean_logprob"],
            tpack["ms_per_step"],
            tpack["train_wall_s"],
            seed,
            cache_build_s=cache_s,
            top_k=DEFAULT_TOP_K,
        ),
    ]


def run_seed_pair(
    c: dict[str, Any],
    out: Path,
    seed: int,
    device,
    vocab: int,
    steps: int,
    *,
    label_prefix: str = "HTPACK",
) -> list[dict[str, Any]]:
    """
    GIVEN shared STAG batches
    WHEN training live STAG vs PRE3 stack (cache then depth-3 train)
    THEN return eval rows gated on ms/step (cache_build reported, not gated).
    """
    live, tpack = train_seed_pair(
        c, out, seed, device, vocab, steps, label_prefix=label_prefix
    )
    rows = eval_seed_rows(c, live, tpack, seed, label_prefix=label_prefix)
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return rows
