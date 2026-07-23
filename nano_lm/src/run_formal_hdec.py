"""Formal equal-budget: B4 fixed BoN vs H-DEC (evolved knobs), 3 seeds."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from decode_bon import decode_bon
from decode_genes import default_bon_gene
from eval_decode import load_pair, score_decode_run
from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_dec import fitness_gene, run_h_dec
from load_model import resolve_device
from matrix_common import ROOT, REPO, write_json
from train_kd import train_kd


def formal_cfg() -> dict[str, Any]:
    return {
        "teacher_id": "roneneldan/TinyStories-33M",
        "tokenizer_id": "EleutherAI/gpt-neo-125M",
        "fit_prompts": ROOT / "prompts/fit_prompts.yaml",
        "prompts": ROOT / "prompts/eval_prompts.yaml",
        "cache": ROOT / ".cache",
        "out": REPO / "results/nano-lm/formal-hdec-b4",
        "steps_kd": 120,
        "max_examples": 300,
        "seq_len": 128,
        "batch_size": 4,
        "lr": 3e-4,
        "seeds": [0, 1, 2],
        "max_new_eval": 48,
        "max_new_fit": 16,
        "dec_pop": 8,
        "dec_gens": 12,
        "bon_n": 4,
    }


def _eval_b4(c: dict[str, Any], ckpt: Path, seed: int) -> dict:
    g = default_bon_gene()
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    prompts = yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    return score_decode_run(
        teacher=teacher,
        student=student,
        prompts=prompts,
        family="B4",
        max_new_tokens=c["max_new_eval"],
        seed=seed,
        temperature=float(g["temperature"]),
        top_p=float(g["top_p"]),
        decode_fn=decode_bon,
        decode_kwargs={"n": int(c["bon_n"])},
        label=f"B4_seed{seed}",
    )


def _eval_hdec_gene(
    c: dict[str, Any], ckpt: Path, gene: dict, seed: int
) -> dict:
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    with c["prompts"].open(encoding="utf-8") as f:
        texts = [p["text"] for p in yaml.safe_load(f)["prompts"]]
    t0 = time.perf_counter()
    lp = fitness_gene(
        gene,
        teacher=teacher,
        student=student,
        prompts=texts,
        max_new=c["max_new_eval"],
        seed=seed + 7777,
    )
    wall_ms = (time.perf_counter() - t0) * 1000.0 / max(1, len(texts))
    return {
        "family": "H-DEC",
        "label": f"HDEC_seed{seed}",
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
        b2 = c["out"] / f"B2_seed{seed}.pt"
        meta = train_kd(
            teacher_id=c["teacher_id"],
            steps=c["steps_kd"],
            batch_size=c["batch_size"],
            seq_len=c["seq_len"],
            max_examples=c["max_examples"],
            lr=c["lr"],
            seed=seed,
            temperature=2.0,
            alpha=0.5,
            tokenizer_id=c["tokenizer_id"],
            cache_dir=c["cache"],
            device=device,
            out_path=b2,
        )
        write_json(c["out"] / f"B2_seed{seed}_train.json", meta)
        rows.append(_eval_b4(c, b2, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()

        meta = run_h_dec(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            cache_dir=c["cache"],
            pop_size=c["dec_pop"],
            generations=c["dec_gens"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_fit"],
            seed=seed,
            out_meta=c["out"] / f"HDEC_seed{seed}_train.json",
        )
        row = _eval_hdec_gene(c, b2, meta["best_gene"], seed)
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
