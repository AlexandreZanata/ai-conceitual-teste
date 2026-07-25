"""Smoke H-CBAT: chunked prefill under BAT vs flat H-BAT (tok/s)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from bat_score import score_batch_early
from cbat_score import DEFAULT_CHUNK, score_batch_cbat, tip_row
from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from eval_decode import load_pair
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


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
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        gene = {**early, "n": 1, "temperature": 1e-6}
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 6262
        bat = score_batch_early(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            max_new=max_new,
            seed=claim,
        )
        bat["n_prompts"] = float(len(prompts))
        rows.append(tip_row("H-BAT", f"HBAT_cbat_seed{seed}", bat, seed, gene))
        cbat = score_batch_cbat(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            max_new=max_new,
            seed=claim,
            chunk_size=DEFAULT_CHUNK,
        )
        cbat["n_prompts"] = float(len(prompts))
        g = {
            **gene,
            "chunk_size": DEFAULT_CHUNK,
            "backend": "sdpa+chunk+bat",
        }
        row = tip_row("H-CBAT", f"HCBAT_seed{seed}", cbat, seed, g)
        write_json(out / f"HCBAT_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "cbat_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": DEFAULT_CHUNK,
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "n=1 near-greedy; long prompts",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "cbat_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
