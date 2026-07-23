"""Formal-budget H-BAND vs H-CASC / H-DECK (matched teacher pulls)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from hold_ops import assert_disjoint, attach_overfit, load_prompt_ids
from hyp_band import run_h_band
from hyp_casc import run_h_casc
from hyp_deck import run_h_deck
from hyp_dec import fitness_gene
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg

# Match H-CASC formal: gens=12, mid_k=3, final_k=1 → 48 gene teacher scores.
N_ARMS = 8
N_PULLS = 48
MID_K = 3
FINAL_K = 1
DECK_TOP_K = 1


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hband"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
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


def _attach(row: dict, meta: dict) -> dict:
    row["teacher_forwards"] = int(meta["teacher_forwards"])
    row["wall_save"] = bool(meta.get("wall_save", False))
    attach_overfit(row, float(meta["best_fit"]))
    return row


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
        common = dict(
            student_ckpt=b2,
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["fit_prompts"],
            cache_dir=c["cache"],
            max_new=c["max_new_fit"],
            eval_max_new=c["max_new_fit"],
        )
        casc = run_h_casc(
            **common,
            pop_size=N_ARMS,
            generations=c["dec_gens"],
            seed=seed,
            mid_k=MID_K,
            final_k=FINAL_K,
            out_meta=c["out"] / f"HCASC_seed{seed}_train.json",
        )
        rows.append(_attach(_eval_gene(c, b2, casc["best_gene"], seed, "H-CASC"), casc))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        deck = run_h_deck(
            **common,
            pop_size=N_ARMS,
            generations=c["dec_gens"],
            seed=seed + 10,
            top_k=DECK_TOP_K,
            out_meta=c["out"] / f"HDECK_seed{seed}_train.json",
        )
        rows.append(_attach(_eval_gene(c, b2, deck["best_gene"], seed, "H-DECK"), deck))
        if device.type == "cuda":
            torch.cuda.empty_cache()
        band = run_h_band(
            **common,
            n_arms=N_ARMS,
            n_pulls=N_PULLS,
            seed=seed + 20,
            out_meta=c["out"] / f"HBAND_seed{seed}_train.json",
        )
        rows.append(_attach(_eval_gene(c, b2, band["best_gene"], seed, "H-BAND"), band))
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
