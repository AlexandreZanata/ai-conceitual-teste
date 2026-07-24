"""Formal H-SHORT: short-draft search vs frozen formal H-EARLY tip."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from hyp_short import run_h_short
from load_model import resolve_device
from matrix_common import REPO, ROOT, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg
from short_fit import fitness_early_detail, fitness_short_detail, tip_row

LAM = 0.4


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hshort"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    base["prompts"] = ROOT / "prompts/eval_prompts.yaml"
    base["short_pop"] = 8
    base["short_gens"] = 6
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def _run_seed(c: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    ckpt = c["ckpt_dir"] / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing shared B2 ckpt: {ckpt}")
    early = _early_gene(c["early_dir"], seed)
    meta = run_h_short(
        student_ckpt=ckpt,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["fit_prompts"],
        eval_prompts_path=c["prompts"],
        cache_dir=c["cache"],
        pop_size=int(c["short_pop"]),
        generations=int(c["short_gens"]),
        max_new=int(c["max_new_fit"]),
        eval_max_new=int(c["max_new_eval"]),
        seed=seed,
        early_gene=early,
        lam=LAM,
        out_meta=c["out"] / f"HSHORT_seed{seed}_train.json",
    )
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    prompts = _texts(c["prompts"])
    claim = seed + 7777
    max_new = int(c["max_new_eval"])
    lp_e, wall_e, gf_e = fitness_early_detail(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    lp_s, wall_s, gf_s = fitness_short_detail(
        meta["best_gene"],
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    gene = dict(meta["best_gene"])
    n_p = len(prompts)
    row_e = tip_row(
        "H-EARLY", f"HEARLY_short_formal_seed{seed}", lp_e, wall_e, gf_e, seed, early
    )
    row_s = tip_row(
        "H-SHORT", f"HSHORT_formal_seed{seed}", lp_s, wall_s, gf_s, seed, gene
    )
    row_e["n_prompts"] = n_p
    row_s["n_prompts"] = n_p
    write_json(c["out"] / f"HSHORT_seed{seed}_eval.json", row_s)
    return [row_e, row_s]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    write_json(
        c["out"] / "formal.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0, "lam": LAM},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
