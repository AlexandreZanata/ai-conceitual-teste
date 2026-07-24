"""Formal-budget H-TYP vs B4 (typical), shared B2 ckpts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_typ import run_h_typ
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import _eval_b4, formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-htyp"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    return base


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        b2 = c["ckpt_dir"] / f"B2_seed{seed}.pt"
        if not b2.is_file():
            raise FileNotFoundError(f"missing shared B2 ckpt: {b2}")
        rows.append(_eval_b4(c, b2, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        meta = run_h_typ(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            eval_prompts_path=c["prompts"],
            cache_dir=c["cache"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_eval"],
            seed=seed,
            out_meta=c["out"] / f"HTYP_seed{seed}_train.json",
        )
        row = {
            "family": "H-TYP",
            "label": f"HTYP_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "best_typ_mass": float(meta["best_typ_mass"]),
            "seed": seed,
        }
        attach_overfit(row, float(meta["best_fit"]))
        rows.append(row)
        if device.type == "cuda":
            torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "config": {k: str(v) if isinstance(v, Path) else v for k, v in c.items()},
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
