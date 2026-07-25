"""Formal H-SHORTB: SHORT under FUSEB vs tip FUSEB (eval, dual budget)."""

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
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hfuseb import formal_cfg as hfuseb_formal_cfg
from short_ops import clamp_short_gene
from shortb_ops import SHORTB_CHUNK
from shortb_score import SMOKE_BUDGETS, score_batch_fuseb, score_batch_shortb, tip_row


def formal_cfg() -> dict[str, Any]:
    base = hfuseb_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hshortb"
    base["short_dir"] = REPO / "results/nano-lm/formal-hshort"
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return {**gene, "n": 1, "temperature": 1e-6}


def _short_gene(short_dir: Path, seed: int, tip: dict[str, Any]) -> dict[str, Any]:
    path = short_dir / f"HSHORT_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal SHORT: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene") or {}
    if "draft_max" not in gene or "stop_conf" not in gene:
        raise ValueError(f"SHORT missing draft_max/stop_conf: {path}")
    return clamp_short_gene(gene, tip)


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


def _run_seed(
    c: dict[str, Any], seed: int, prompts: list[str]
) -> list[dict[str, Any]]:
    ckpt = c["ckpt_dir"] / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing shared B2 ckpt: {ckpt}")
    gene = _early_gene(c["early_dir"], seed)
    short = _short_gene(c["short_dir"], seed, gene)
    thr = _kv_threshold(c["kvsel_dir"], seed)
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    claim = seed + 9606
    fuseb = score_batch_fuseb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        seed=claim,
        kv_threshold=thr,
        chunk_size=SHORTB_CHUNK,
    )
    shortb = score_batch_shortb(
        teacher=teacher,
        student=student,
        prompts=prompts,
        gene=gene,
        short=short,
        seed=claim,
        kv_threshold=thr,
        chunk_size=SHORTB_CHUNK,
    )
    g_tip = {
        **gene,
        "kv_threshold": thr,
        "chunk_size": SHORTB_CHUNK,
        "backend": "sdpa+kvsel+chbat",
    }
    g = {
        **gene,
        "draft_max": short["draft_max"],
        "stop_conf": short["stop_conf"],
        "kv_threshold": thr,
        "chunk_size": SHORTB_CHUNK,
        "backend": "sdpa+kvsel+short+chbat",
    }
    return [
        tip_row("H-FUSEB", f"HFUSEB_shortb_formal_seed{seed}", fuseb, seed, g_tip),
        tip_row("H-SHORTB", f"HSHORTB_formal_seed{seed}", shortb, seed, g),
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
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed, prompts))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "n_prompts": len(prompts),
        "chunk_size": SHORTB_CHUNK,
        "budgets": list(SMOKE_BUDGETS),
        "target_tokens": LONG_TARGET_TOKENS,
        "mode": "dual-budget SHORT under FUSEB; n=1 near-greedy; long eval",
    }
    write_json(c["out"] / "formal.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
