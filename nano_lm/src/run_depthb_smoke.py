"""Smoke H-DEPTHB: DEPTH_prun ckpt under LAYB vs tip LAYB on B2."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from depthb_ops import DEPTHB_CHUNK
from eval_decode import load_pair
from eval_student import load_student_ckpt
from lay_ops import clamp_lay_gene
from layb_score import SMOKE_BUDGETS, score_batch_layb, tip_row
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from prun_mask import density_of
from student_model import build_depth_student


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _lay_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HLAY_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing LAY util: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "max_skip" not in gene or "lay_conf" not in gene:
        raise ValueError(f"LAY missing max_skip/lay_conf: {path}")
    return clamp_lay_gene(gene)


def _kv_threshold(out: Path, seed: int) -> int:
    path = out / f"HKVSEL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing KVSEL util: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "kv_threshold" not in gene:
        raise ValueError(f"KVSEL missing kv_threshold: {path}")
    return int(gene["kv_threshold"])


def _load_texts(*paths: Path) -> list[str]:
    texts: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            texts.extend(p["text"] for p in yaml.safe_load(f)["prompts"])
    return texts


def _scale_gflops(metrics: dict[str, float], dens: float) -> dict[str, float]:
    out = dict(metrics)
    out["mean_gflops"] = float(metrics["mean_gflops"]) * float(dens)
    return out


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    from data_tiny import load_tokenizer

    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    raw = _load_texts(c["prompts"], c["fit_prompts"])
    prompts = long_prompts(raw, tok, target_tokens=LONG_TARGET_TOKENS)
    teacher = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        lay = _lay_gene(out, seed)
        thr = _kv_threshold(out, seed)
        gene = {**early, "n": 1, "temperature": 1e-6}
        claim = seed + 6969
        _, b2 = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        layb = score_batch_layb(
            teacher=teacher,
            student=b2,
            prompts=prompts,
            gene=gene,
            lay=lay,
            seed=claim,
            kv_threshold=thr,
            chunk_size=DEPTHB_CHUNK,
        )
        g_tip = {
            **gene,
            **lay,
            "kv_threshold": thr,
            "chunk_size": DEPTHB_CHUNK,
            "backend": "sdpa+kvsel+lay+chbat",
            "ckpt": "B2",
        }
        rows.append(tip_row("H-LAYB", f"HLAYB_depthb_seed{seed}", layb, seed, g_tip))
        depth_ckpt = out / f"HDEPTH_prun_seed{seed}.pt"
        if not depth_ckpt.is_file():
            raise FileNotFoundError(f"missing DEPTH_prun ckpt: {depth_ckpt}")
        depth = load_student_ckpt(
            depth_ckpt, teacher.tokenizer, teacher.device, build_fn=build_depth_student
        )
        dens = density_of(depth)
        depthb = _scale_gflops(
            score_batch_layb(
                teacher=teacher,
                student=depth,
                prompts=prompts,
                gene=gene,
                lay=lay,
                seed=claim,
                kv_threshold=thr,
                chunk_size=DEPTHB_CHUNK,
            ),
            dens,
        )
        g = {
            **gene,
            **lay,
            "kv_threshold": thr,
            "chunk_size": DEPTHB_CHUNK,
            "backend": "sdpa+kvsel+lay+chbat",
            "ckpt": "HDEPTH_prun",
            "density": dens,
        }
        row = tip_row("H-DEPTHB", f"HDEPTHB_seed{seed}", depthb, seed, g)
        row["density"] = dens
        write_json(out / f"HDEPTHB_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "depthb_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": DEPTHB_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "DEPTH_prun under LAYB vs B2+LAYB; dual-budget; long prompts",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "depthb_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
