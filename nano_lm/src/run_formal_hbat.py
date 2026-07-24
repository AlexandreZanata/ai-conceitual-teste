"""Formal H-BAT: tip EARLY exit knobs, batched vs serial (eval_prompts)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from bat_score import score_batch_early, score_serial_early, tip_row
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, ROOT, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hbat"
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
    # Deterministic tip-exit policy: keep exit knobs; freeze n/temp for lp fidelity.
    return {
        **gene,
        "n": 1,
        "temperature": 1e-6,
    }


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def _run_seed(c: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    ckpt = c["ckpt_dir"] / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing shared B2 ckpt: {ckpt}")
    gene = _early_gene(c["early_dir"], seed)
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    prompts = _texts(c["prompts"])
    claim = seed + 9001
    serial = score_serial_early(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=int(c["max_new_eval"]),
        seed=claim,
    )
    serial["n_prompts"] = float(len(prompts))
    batched = score_batch_early(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        max_new=int(c["max_new_eval"]),
        seed=claim,
    )
    batched["n_prompts"] = float(len(prompts))
    return [
        tip_row("H-EARLY", f"HEARLY_bat_formal_seed{seed}", serial, seed, gene),
        tip_row("H-BAT", f"HBAT_formal_seed{seed}", batched, seed, gene),
    ]


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
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "n_prompts": len(_texts(c["prompts"])),
        "mode": "tip-exit knobs; n=1 near-greedy",
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
