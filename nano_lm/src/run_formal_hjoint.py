"""Formal-budget H-JOINT vs CURL + EARLY@B2 (fit≠eval)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_early import run_h_early
from hyp_joint import run_h_joint
from lat2_ops import MIN_LAM
from load_model import resolve_device
from matrix_common import REPO, eval_ckpt, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hjoint"
    base["curl_dir"] = REPO / "results/nano-lm/formal-hcurl"
    base["b2_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["steps_kd"] = 120
    base["seq_len"] = 128
    base["batch_size"] = 4
    base["max_examples"] = 300
    return base


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        curl = c["curl_dir"] / f"HCURL_lo8_seed{seed}.pt"
        b2 = c["b2_dir"] / f"B2_seed{seed}.pt"
        if not curl.is_file() or not b2.is_file():
            raise FileNotFoundError(f"missing formal ckpt seed={seed}")
        rows.append(eval_ckpt(c, curl, seed, "H-CURL"))
        early = run_h_early(
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
            out_meta=c["out"] / f"HEARLY_B2_seed{seed}_train.json",
        )
        rows.append(
            {
                "family": "H-EARLY",
                "label": f"HEARLY_seed{seed}",
                "teacher_mean_logprob": float(early["eval_fit"]),
                "mean_wall_ms": float(early["eval_wall_ms"]),
                "seed": seed,
                "ckpt_source": "B2",
            }
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
        # Formal joint uses eval prompts via matrix cfg override.
        jc = dict(c)
        jc["prompts"] = c["fit_prompts"]
        meta = run_h_joint(
            c=jc,
            device=device,
            seed=seed,
            out_dir=c["out"],
            pop_size=c["dec_pop"],
            generations=c["dec_gens"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_fit"],
            lam=MIN_LAM,
        )
        # Re-claim on eval prompts would need hyp_joint eval_path; smoke-first.
        row = {
            "family": "H-JOINT",
            "label": f"HJOINT_seed{seed}",
            "teacher_mean_logprob": float(meta["eval_fit"]),
            "mean_wall_ms": float(meta["eval_wall_ms"]),
            "best_gene": meta["best_gene"],
            "seed": seed,
            "ckpt_source": "JOINT_bank",
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
