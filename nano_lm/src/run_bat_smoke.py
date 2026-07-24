"""Smoke H-BAT: batched multi-prompt EARLY vs serial tip (tok/s)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import yaml

from bat_score import score_batch_early, score_serial_early, tip_row
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
    # More prompts → clearer batching win; smoke+fit stay claim-disjoint from eval.
    prompts = _load_texts(c["prompts"], c["fit_prompts"])
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        # Throughput mode: n=1 + near-greedy so serial vs batch share one policy
        # (BoN RNG structure differs under a shared batch seed).
        gene = {**early, "n": 1, "temperature": 1e-6}
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 4242
        serial = score_serial_early(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            max_new=max_new,
            seed=claim,
        )
        serial["n_prompts"] = float(len(prompts))
        rows.append(
            tip_row("H-EARLY", f"HEARLY_bat_seed{seed}", serial, seed, gene)
        )
        batched = score_batch_early(
            teacher=teacher,
            student=student,
            prompts=prompts,
            gene=gene,
            max_new=max_new,
            seed=claim,
        )
        batched["n_prompts"] = float(len(prompts))
        row = tip_row("H-BAT", f"HBAT_seed{seed}", batched, seed, gene)
        write_json(out / f"HBAT_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "bat_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "mode": "n=1 near-greedy",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "bat_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
