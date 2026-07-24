"""Smoke H-TOP: top-k soft-label cache vs live STAG (train step time)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from load_model import load_causal_lm, resolve_device
from matrix_common import eval_ckpt, matrix_cfg, write_json
from soft_cache import plan_cur_batches
from soft_train import train_live_batches
from stag_ops import STAG_SEQ_LO
from top_cache import build_topk_cache, load_topk_cache
from top_ops import DEFAULT_TOP_K
from top_train import train_topk_cache

TIP_STAGES = 4


def _row(
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


def _run_seed(
    c: dict[str, Any], out: Path, seed: int, device, vocab: int, steps: int
) -> list[dict[str, Any]]:
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
    cache_path = out / f"HTOP_seed{seed}_cache.pt"
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    cache_meta = build_topk_cache(
        teacher=teacher,
        batches=batches,
        out_path=cache_path,
        top_k=DEFAULT_TOP_K,
    )
    write_json(out / f"HTOP_seed{seed}_cache.json", cache_meta)
    live = train_live_batches(
        teacher=teacher,
        batches=batches,
        device=device,
        lr=c["lr"],
        seed=seed + 101,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"HTOP_live_seed{seed}.pt",
    )
    write_json(out / f"HTOP_live_seed{seed}_train.json", live)
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
        out_path=out / f"HTOP_seed{seed}.pt",
    )
    top["cache_build_s"] = cache_meta["cache_build_s"]
    top["top_k"] = DEFAULT_TOP_K
    write_json(out / f"HTOP_seed{seed}_train.json", top)
    ev_l = eval_ckpt(c, Path(live["out_path"]), seed, "H-STAG")
    ev_t = eval_ckpt(c, Path(top["out_path"]), seed, "H-TOP")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        _row(
            "H-STAG",
            f"HTOP_live_seed{seed}",
            ev_l["teacher_mean_logprob"],
            live["ms_per_step"],
            live["train_wall_s"],
            seed,
        ),
        _row(
            "H-TOP",
            f"HTOP_seed{seed}",
            ev_t["teacher_mean_logprob"],
            top["ms_per_step"],
            top["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
            top_k=DEFAULT_TOP_K,
        ),
    ]


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c.get("steps_cur", c["steps_kd"]))
    vocab = len(load_tokenizer(c["tokenizer_id"], c["cache"]))
    t0 = time.perf_counter()
    rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, out, seed, device, vocab, steps))
    write_json(
        out / "top_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k": DEFAULT_TOP_K,
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "top_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
