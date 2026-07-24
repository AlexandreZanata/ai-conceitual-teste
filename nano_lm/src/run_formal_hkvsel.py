"""Formal H-KVSEL: gated KV vs eager on formal EARLY tip (dual budget)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from kvsel_fit import (
    fitness_early_dual,
    pick_kvsel_threshold,
    tip_row,
    warmup_kvsel,
)
from kvsel_ops import SMOKE_BUDGETS, SMOKE_THRESHOLDS
from lat_ops import EPS_LP
from load_model import resolve_device
from matrix_common import REPO, ROOT, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hkvsel"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    base["prompts"] = ROOT / "prompts/eval_prompts.yaml"
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
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    prompts = _texts(c["prompts"])
    claim = seed + 9191
    warmup_kvsel(early, teacher=teacher, student=student, prompts=prompts)
    lp_e, wall_e, gf_e = fitness_early_dual(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        seed=claim,
    )
    tip = tip_row(
        "H-EARLY",
        f"HEARLY_kvsel_formal_seed{seed}",
        lp_e,
        wall_e,
        gf_e,
        seed,
        early,
    )
    tip["n_prompts"] = len(prompts)
    tip["budgets"] = list(SMOKE_BUDGETS)
    thr, lp_k, wall_k, gf_k = pick_kvsel_threshold(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        seed=claim,
        thresholds=SMOKE_THRESHOLDS,
        tip_lp=lp_e,
        tip_wall=wall_e,
        eps_lp=EPS_LP,
    )
    gene = {**early, "kv_threshold": thr}
    row = tip_row(
        "H-KVSEL", f"HKVSEL_formal_seed{seed}", lp_k, wall_k, gf_k, seed, gene
    )
    row["n_prompts"] = len(prompts)
    row["budgets"] = list(SMOKE_BUDGETS)
    write_json(c["out"] / f"HKVSEL_seed{seed}_eval.json", row)
    return [tip, row]


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
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "budgets": list(SMOKE_BUDGETS),
            "thresholds": list(SMOKE_THRESHOLDS),
            "n_prompts": len(_texts(c["prompts"])),
        },
    )
    print(
        json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
