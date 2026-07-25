"""Smoke H-FCPOOLB: FUSE (FLASH⊕KVSEL) under CPOOLB vs tip CPOOLB."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from eval_decode import load_pair
from fcpoolb_ops import FCPOOLB_CHUNK
from fcpoolb_score import (
    SMOKE_BUDGETS,
    score_batch_cpoolb_dual,
    score_batch_fcpoolb,
    tip_row,
)
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from poolb_score import throughput_gene


def _pool_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HPOOL_seed{seed}_eval.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing POOL tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"POOL missing best_gene: {path}")
    return gene


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
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        tip = _pool_gene(out, seed)
        thr = _kv_threshold(out, seed)
        gene = throughput_gene(tip)
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 6666
        cpoolb = score_batch_cpoolb_dual(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            seed=claim,
            chunk_size=FCPOOLB_CHUNK,
        )
        g_tip = {
            **gene,
            "chunk_size": FCPOOLB_CHUNK,
            "backend": "sdpa+chunk+poolb",
        }
        rows.append(
            tip_row("H-CPOOLB", f"HCPOOLB_fcpoolb_seed{seed}", cpoolb, seed, g_tip)
        )
        fcpoolb = score_batch_fcpoolb(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            seed=claim,
            kv_threshold=thr,
            chunk_size=FCPOOLB_CHUNK,
        )
        g = {
            **gene,
            "kv_threshold": thr,
            "chunk_size": FCPOOLB_CHUNK,
            "backend": "sdpa+kvsel+cpoolb",
        }
        row = tip_row("H-FCPOOLB", f"HFCPOOLB_seed{seed}", fcpoolb, seed, g)
        write_json(out / f"HFCPOOLB_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "fcpoolb_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": FCPOOLB_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "dual-budget FUSE under CPOOLB; n=1 near-greedy; long prompts",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "fcpoolb_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
