"""Smoke H-SOFT: offline soft-label cache vs live STAG (train step time)."""

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
from soft_cache import build_soft_cache, load_soft_cache, plan_cur_batches
from soft_train import train_live_batches, train_soft_cache
from stag_ops import STAG_SEQ_LO

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
) -> dict[str, Any]:
    return {
        "family": family,
        "label": label,
        "teacher_mean_logprob": float(lp),
        "mean_ms_step": float(ms_step),
        "train_wall_s": float(train_wall_s),
        "cache_build_s": float(cache_build_s),
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
        seed=seed + 91,
    )
    cache_path = out / f"HSOFT_seed{seed}_cache.pt"
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    cache_meta = build_soft_cache(
        teacher=teacher, batches=batches, out_path=cache_path
    )
    write_json(out / f"HSOFT_seed{seed}_cache.json", cache_meta)
    live = train_live_batches(
        teacher=teacher,
        batches=batches,
        device=device,
        lr=c["lr"],
        seed=seed + 91,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"HSOFT_live_seed{seed}.pt",
    )
    write_json(out / f"HSOFT_live_seed{seed}_train.json", live)
    del teacher
    if device.type == "cuda":
        torch.cuda.empty_cache()
    soft = train_soft_cache(
        records=load_soft_cache(cache_path),
        vocab_size=vocab,
        device=device,
        lr=c["lr"],
        seed=seed + 91,
        temperature=2.0,
        alpha=0.5,
        out_path=out / f"HSOFT_seed{seed}.pt",
    )
    soft["cache_build_s"] = cache_meta["cache_build_s"]
    write_json(out / f"HSOFT_seed{seed}_train.json", soft)
    ev_l = eval_ckpt(c, Path(live["out_path"]), seed, "H-STAG")
    ev_s = eval_ckpt(c, Path(soft["out_path"]), seed, "H-SOFT")
    if device.type == "cuda":
        torch.cuda.empty_cache()
    return [
        _row(
            "H-STAG",
            f"HSOFT_live_seed{seed}",
            ev_l["teacher_mean_logprob"],
            live["ms_per_step"],
            live["train_wall_s"],
            seed,
        ),
        _row(
            "H-SOFT",
            f"HSOFT_seed{seed}",
            ev_s["teacher_mean_logprob"],
            soft["ms_per_step"],
            soft["train_wall_s"],
            seed,
            cache_build_s=float(cache_meta["cache_build_s"]),
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
        out / "soft_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "soft_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
