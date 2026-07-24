"""Formal-budget H-THIN vs H-CURL (same EARLY decode)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from cur_ops import N_STAGES
from early_fit import fitness_early_detail
from eval_student import load_student_ckpt
from hold_ops import assert_disjoint, load_prompt_ids
from hyp_cur import run_h_cur
from load_model import resolve_device
from matrix_common import ROOT, REPO, write_json
from run_formal_hcurl import formal_cfg as hcurl_formal_cfg
from student_model import build_student, build_thin_student


def formal_cfg() -> dict[str, Any]:
    base = hcurl_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hthin"
    base["curl_dir"] = REPO / "results/nano-lm/formal-hcurl"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    return base


def _gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    meta = json.loads(path.read_text(encoding="utf-8"))
    gene = meta.get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"formal EARLY missing best_gene: {path}")
    return gene


def _score_row(
    c: dict[str, Any],
    *,
    family: str,
    ckpt: Path,
    gene: dict,
    seed: int,
    build_fn: Any,
) -> dict:
    from load_model import load_causal_lm

    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    student = load_student_ckpt(
        ckpt, teacher.tokenizer, teacher.device, build_fn=build_fn
    )
    texts = [
        p["text"]
        for p in yaml.safe_load(c["prompts"].read_text(encoding="utf-8"))["prompts"]
    ]
    lp, wall = fitness_early_detail(
        gene,
        teacher=teacher,
        student=student,
        prompts=texts,
        max_new=c["max_new_eval"],
        seed=seed + 7777,
    )
    return {
        "family": family,
        "label": f"{family.replace('-', '')}_seed{seed}",
        "teacher_mean_logprob": float(lp),
        "mean_wall_ms": float(wall),
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
        curl = c["curl_dir"] / f"HCURL_lo8_seed{seed}.pt"
        if not curl.is_file():
            raise FileNotFoundError(f"missing formal CURL ckpt: {curl}")
        thin = c["out"] / f"HTHIN_lo8_seed{seed}.pt"
        if not thin.is_file():
            run_h_cur(
                teacher_id=c["teacher_id"],
                tokenizer_id=c["tokenizer_id"],
                cache_dir=c["cache"],
                device=device,
                steps=c["steps_kd"],
                batch_size=c["batch_size"],
                seq_len=c["seq_len"],
                max_examples=c["max_examples"],
                lr=c["lr"],
                seed=seed + 97,
                temperature=2.0,
                alpha=0.5,
                out_path=thin,
                seq_lo=8,
                n_stages=N_STAGES,
                build_fn=build_thin_student,
                hypothesis="H-THIN",
            )
        gene = _gene(c["early_dir"], seed)
        rows.append(
            _score_row(
                c, family="H-CURL", ckpt=curl, gene=gene, seed=seed, build_fn=build_student
            )
        )
        rows.append(
            _score_row(
                c,
                family="H-THIN",
                ckpt=thin,
                gene=gene,
                seed=seed,
                build_fn=build_thin_student,
            )
        )
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
