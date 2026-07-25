"""Formal H-Q4: CUDA int4 on formal DEPTH_prun vs fp control."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, ROOT, write_json
from q4_fit import DEFAULT_GROUP, DEFAULT_TILES, score_pair
from run_formal_hdepth import formal_cfg as hdepth_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hdepth_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hq4"
    base["depth_dir"] = REPO / "results/nano-lm/formal-hdepth"
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


def _run_seed(
    c: dict[str, Any],
    seed: int,
    prompts: list[str],
    teacher: object,
) -> list[dict]:
    ckpt = c["depth_dir"] / f"HDEPTH_prun_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing formal DEPTH_prun: {ckpt}")
    early = _early_gene(c["early_dir"], seed)
    depth_row, q4_row = score_pair(
        early,
        ckpt=ckpt,
        teacher=teacher,
        prompts=prompts,
        max_new=int(c["max_new_eval"]),
        seed=seed,
        claim=seed + 4141,
    )
    depth_row["label"] = f"HDEPTH_q4_formal_seed{seed}"
    q4_row["label"] = f"HQ4_formal_seed{seed}"
    for r in (depth_row, q4_row):
        r["n_prompts"] = len(prompts)
    write_json(c["out"] / f"HQ4_seed{seed}_eval.json", q4_row)
    return [depth_row, q4_row]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-Q4 formal requires CUDA")
    c["out"].mkdir(parents=True, exist_ok=True)
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    prompts = _texts(c["prompts"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed, prompts, teacher))
        torch.cuda.empty_cache()
    write_json(
        c["out"] / "formal.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "groupsize": DEFAULT_GROUP,
            "tiles": DEFAULT_TILES,
            "backend": "aten_int4pack_cuda",
            "ckpt": "formal HDEPTH_prun",
            "n_prompts": len(prompts),
        },
    )
    print(
        json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
