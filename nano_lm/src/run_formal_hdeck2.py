"""Formal-budget H-DECK2: top_k∈{1,2,3} on shared B2 ckpts (reuse H-DECK KD)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from deck2_ops import DECK2_TOP_KS
from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_deck import run_h_deck
from hyp_dec import fitness_gene
from load_model import resolve_device
from matrix_common import ROOT, REPO, write_json
from run_formal_hdeck import _eval_b4, formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hdeck2"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    return base


def _eval_gene(
    c: dict[str, Any], ckpt: Path, gene: dict, seed: int, top_k: int
) -> dict:
    from eval_decode import load_pair

    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    t0 = time.perf_counter()
    lp = fitness_gene(
        gene,
        teacher=teacher,
        student=student,
        prompts=texts,
        max_new=c["max_new_eval"],
        seed=seed + 7777 + top_k,
    )
    wall_ms = (time.perf_counter() - t0) * 1000.0 / max(1, len(texts))
    return {
        "family": "H-DECK2",
        "label": f"HDECK2_k{top_k}_seed{seed}",
        "top_k": top_k,
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": wall_ms,
        "n_prompts": len(texts),
        "seed": seed,
        "best_gene": gene,
    }


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
        for top_k in DECK2_TOP_KS:
            meta = run_h_deck(
                student_ckpt=b2,
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                prompts_path=c["fit_prompts"],
                cache_dir=c["cache"],
                pop_size=c["dec_pop"],
                generations=c["dec_gens"],
                max_new=c["max_new_fit"],
                eval_max_new=c["max_new_fit"],
                seed=seed + 100 * top_k,
                top_k=top_k,
                out_meta=c["out"] / f"HDECK2_k{top_k}_seed{seed}_train.json",
            )
            row = _eval_gene(c, b2, meta["best_gene"], seed, top_k)
            row["wall_save"] = bool(meta["wall_save"])
            row["teacher_forwards"] = int(meta["teacher_forwards"])
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
