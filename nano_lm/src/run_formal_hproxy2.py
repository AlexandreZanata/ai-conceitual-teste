"""Formal-budget H-PROXY2 vs H-DECK (CE vs self-lp), top_k=1, shared B2."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_deck import run_h_deck
from hyp_dec import fitness_gene
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg

TOP_K = 1


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hproxy2"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["deck_top_k"] = TOP_K
    return base


def _eval_gene(
    c: dict[str, Any], ckpt: Path, gene: dict, seed: int, family: str
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
        seed=seed + 7777,
    )
    wall_ms = (time.perf_counter() - t0) * 1000.0 / max(1, len(texts))
    return {
        "family": family,
        "label": f"{family.replace('-', '')}_seed{seed}",
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
        for family, proxy, tag in (
            ("H-DECK", "self_lp", "HDECK"),
            ("H-PROXY2", "ce", "HPROXY2"),
        ):
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
                seed=seed + (0 if proxy == "self_lp" else 50),
                top_k=TOP_K,
                proxy=proxy,
                hypothesis=family,
                out_meta=c["out"] / f"{tag}_seed{seed}_train.json",
            )
            row = _eval_gene(c, b2, meta["best_gene"], seed, family)
            row["wall_save"] = bool(meta["wall_save"])
            row["teacher_forwards"] = int(meta["teacher_forwards"])
            row["proxy"] = proxy
            row["top_k"] = TOP_K
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
