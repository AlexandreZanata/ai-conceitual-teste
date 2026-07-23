"""Formal-budget H-DECQ vs B4 + same-run H-DECM, shared B2 ckpts."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from decm_ops import MIX_M
from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_decm import run_h_decm
from hyp_decq import run_h_decq
from lat2_ops import MIN_LAM
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import _eval_b4, formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hdecq"
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
        common = dict(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            eval_prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=c["dec_pop"],
            generations=c["dec_gens"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_eval"],
            seed=seed,
            lam=MIN_LAM,
            mix_m=MIX_M,
        )
        decm = run_h_decm(**common, out_meta=c["out"] / f"HDECM_qctrl_seed{seed}.json")
        n_eval = len(load_prompt_ids(c["prompts"]))
        rows.append(
            {
                "family": "H-DECM",
                "label": f"HDECM_qctrl_seed{seed}",
                "teacher_mean_logprob": float(decm["eval_fit"]),
                "mean_wall_ms": float(decm["eval_wall_ms"]),
                "n_prompts": n_eval,
                "seed": seed,
            }
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
        decq = run_h_decq(**common, out_meta=c["out"] / f"HDECQ_seed{seed}_train.json")
        row = {
            "family": "H-DECQ",
            "label": f"HDECQ_seed{seed}",
            "teacher_mean_logprob": float(decq["eval_fit"]),
            "mean_wall_ms": float(decq["eval_wall_ms"]),
            "n_prompts": n_eval,
            "seed": seed,
            "mix_m": MIX_M,
            "picks": decq["picks"],
        }
        attach_overfit(row, float(decq["best_fit"]))
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
