"""Formal H-PRUNB: PRUN under LAYB vs tip LAYB on B2 (eval)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from data_tiny import load_tokenizer
from eval_decode import load_pair
from eval_student import load_student_ckpt
from hold_ops import assert_disjoint, load_prompt_ids
from lay_ops import clamp_lay_gene
from layb_score import SMOKE_BUDGETS, score_batch_layb, tip_row
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, write_json
from prun_mask import density_of
from prunb_ops import PRUNB_CHUNK
from run_formal_hlayb import formal_cfg as hlayb_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hlayb_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hprunb"
    base["prun_dir"] = REPO / "results/nano-lm/formal-hprun"
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return {**gene, "n": 1, "temperature": 1e-6}


def _lay_gene(lay_dir: Path, seed: int) -> dict[str, Any]:
    path = lay_dir / f"HLAY_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal LAY: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "max_skip" not in gene or "lay_conf" not in gene:
        raise ValueError(f"LAY missing max_skip/lay_conf: {path}")
    return clamp_lay_gene(gene)


def _kv_threshold(kvsel_dir: Path, seed: int) -> int:
    path = kvsel_dir / f"HKVSEL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal KVSEL: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {path}")
    return int(gene["kv_threshold"])


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def _scale_gflops(metrics: dict[str, float], dens: float) -> dict[str, float]:
    out = dict(metrics)
    out["mean_gflops"] = float(metrics["mean_gflops"]) * float(dens)
    return out


def _run_seed(
    c: dict[str, Any], seed: int, prompts: list[str], teacher: Any
) -> list[dict[str, Any]]:
    ckpt = c["ckpt_dir"] / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing shared B2 ckpt: {ckpt}")
    prun_ckpt = c["prun_dir"] / f"HPRUN_seed{seed}.pt"
    if not prun_ckpt.is_file():
        raise FileNotFoundError(f"missing formal PRUN: {prun_ckpt}")
    gene = _early_gene(c["early_dir"], seed)
    lay = _lay_gene(c["lay_dir"], seed)
    thr = _kv_threshold(c["kvsel_dir"], seed)
    _, b2 = load_pair(ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"])
    claim = seed + 9808
    layb = score_batch_layb(
        teacher=teacher,
        student=b2,
        prompts=prompts,
        gene=gene,
        lay=lay,
        seed=claim,
        kv_threshold=thr,
        chunk_size=PRUNB_CHUNK,
    )
    prun = load_student_ckpt(prun_ckpt, teacher.tokenizer, teacher.device)
    dens = density_of(prun)
    prunb = _scale_gflops(
        score_batch_layb(
            teacher=teacher,
            student=prun,
            prompts=prompts,
            gene=gene,
            lay=lay,
            seed=claim,
            kv_threshold=thr,
            chunk_size=PRUNB_CHUNK,
        ),
        dens,
    )
    g_tip = {
        **gene,
        **lay,
        "kv_threshold": thr,
        "chunk_size": PRUNB_CHUNK,
        "backend": "sdpa+kvsel+lay+chbat",
        "ckpt": "B2",
    }
    g = {
        **gene,
        **lay,
        "kv_threshold": thr,
        "chunk_size": PRUNB_CHUNK,
        "backend": "sdpa+kvsel+lay+chbat",
        "ckpt": "HPRUN",
        "density": dens,
    }
    row = tip_row("H-PRUNB", f"HPRUNB_formal_seed{seed}", prunb, seed, g)
    row["density"] = dens
    return [
        tip_row("H-LAYB", f"HLAYB_prunb_formal_seed{seed}", layb, seed, g_tip),
        row,
    ]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        _texts(c["prompts"]), tok, target_tokens=LONG_TARGET_TOKENS
    )
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed, prompts, teacher))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "n_prompts": len(prompts),
        "chunk_size": PRUNB_CHUNK,
        "budgets": list(SMOKE_BUDGETS),
        "target_tokens": LONG_TARGET_TOKENS,
        "mode": "PRUN under LAYB vs B2+LAYB; dual-budget; long eval",
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
