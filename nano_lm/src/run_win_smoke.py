"""Smoke H-WIN: local-window student under STAG recipe vs H-STAG tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from hyp_cur import run_h_cur
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from stag_ops import STAG_SEQ_LO
from student_model import build_student
from win_fit import score_ar_win
from win_ops import DEFAULT_WINDOW, TIP_STAGES
from win_student import build_win_student


def _prompts(path: Path) -> list[str]:
    with path.open(encoding="utf-8") as f:
        return [p["text"] for p in yaml.safe_load(f)["prompts"]]


def _tip_ckpt(out: Path, seed: int) -> Path:
    path = out / f"HSTAG_st{TIP_STAGES}_seed{seed}.pt"
    if not path.is_file():
        raise FileNotFoundError(f"missing STAG tip: {path}")
    return path


def _train_win(c: dict[str, Any], out: Path, seed: int, device) -> Path:
    ckpt = out / f"HWIN_seed{seed}.pt"
    if ckpt.is_file():
        return ckpt
    steps = int(c.get("steps_cur", c["steps_kd"]))
    meta = run_h_cur(
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        device=device,
        steps=steps,
        batch_size=c["batch_size"],
        seq_len=c["seq_len"],
        max_examples=c["max_examples"],
        lr=c["lr"],
        seed=seed + 73,
        temperature=2.0,
        alpha=0.5,
        out_path=ckpt,
        seq_lo=STAG_SEQ_LO,
        n_stages=TIP_STAGES,
        build_fn=build_win_student,
        hypothesis="H-WIN",
    )
    meta["window"] = DEFAULT_WINDOW
    write_json(out / f"HWIN_seed{seed}_train.json", meta)
    return ckpt


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = _prompts(c["prompts"])
    max_new = int(c["max_new_eval"])
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        tip = _tip_ckpt(out, seed)
        win_ckpt = _train_win(c, out, seed, device)
        tip_row = score_ar_win(
            ckpt=tip,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            decode_seed=seed + 7777,
            build_fn=build_student,
            family="H-STAG",
            label=f"HSTAG_win_seed{seed}",
            window=None,
        )
        rows.append(tip_row)
        win_row = score_ar_win(
            ckpt=win_ckpt,
            teacher=teacher,
            prompts=prompts,
            max_new=max_new,
            seed=seed,
            decode_seed=seed + 7777,
            build_fn=build_win_student,
            family="H-WIN",
            label=f"HWIN_seed{seed}",
            window=DEFAULT_WINDOW,
        )
        write_json(out / f"HWIN_seed{seed}_eval.json", win_row)
        rows.append(win_row)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    write_json(
        out / "win_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "window": DEFAULT_WINDOW,
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "win_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
