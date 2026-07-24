"""Smoke H-KVSEL: gated KV vs eager H-EARLY (dual budget mean)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from eval_decode import load_pair
from flop_score import load_prompts
from kvsel_fit import (
    fitness_early_dual,
    pick_kvsel_threshold,
    tip_row,
    warmup_kvsel,
)
from kvsel_ops import SMOKE_BUDGETS, SMOKE_THRESHOLDS
from lat_ops import EPS_LP
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


def main() -> int:
    c = matrix_cfg()
    resolve_device(True)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = [p["text"] for p in load_prompts(c["prompts"])]
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim = seed + 9090
        warmup_kvsel(
            early, teacher=teacher, student=student, prompts=prompts
        )
        lp_e, wall_e, gf_e = fitness_early_dual(
            early,
            teacher=teacher,
            student=student,
            prompts=prompts,
            seed=claim,
        )
        tip = tip_row(
            "H-EARLY",
            f"HEARLY_kvsel_seed{seed}",
            lp_e,
            wall_e,
            gf_e,
            seed,
            early,
        )
        tip["budgets"] = list(SMOKE_BUDGETS)
        rows.append(tip)
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
            "H-KVSEL", f"HKVSEL_seed{seed}", lp_k, wall_k, gf_k, seed, gene
        )
        row["budgets"] = list(SMOKE_BUDGETS)
        write_json(out / f"HKVSEL_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "kvsel_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "budgets": list(SMOKE_BUDGETS),
            "thresholds": list(SMOKE_THRESHOLDS),
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "kvsel_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
