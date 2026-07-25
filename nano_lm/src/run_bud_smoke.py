"""Smoke H-BUD: hard wall/GFLOPs budgets — which recipes survive vs tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from bud_ops import DELTA_GFLOPS_FRAC, decide_hbud
from bud_score import budget_verdicts
from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from data_tiny import load_tokenizer
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from pack_ops import PACK_CHUNK
from pack_pair import SMOKE_BUDGETS, run_seed_trio
from qpack_ops import QPACK_CHUNK
from qpack_pair import run_seed_pair as run_qpack_pair
from tpack_pair import run_seed_pair as run_tpack_pair


def _texts(*paths: Path) -> list[str]:
    out: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            out.extend(p["text"] for p in yaml.safe_load(f)["prompts"])
    return out


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-BUD requires CUDA", file=sys.stderr)
        return 2
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        _texts(c["prompts"], c["fit_prompts"]), tok, target_tokens=LONG_TARGET_TOKENS
    )
    t0 = time.perf_counter()
    pack_rows: list[dict[str, Any]] = []
    qpack_rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "serve", "seed": seed}), flush=True)
        pack_rows.extend(run_seed_trio(c, seed, prompts, claim_offset=9500))
        qpack_rows.extend(run_qpack_pair(c, seed, prompts, claim_offset=9530))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    steps = int(c.get("steps_cur", c["steps_kd"]))
    vocab = len(tok)
    tpack_rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "tpack", "seed": seed}), flush=True)
        tpack_rows.extend(
            run_tpack_pair(c, out, seed, device, vocab, steps, label_prefix="HBUD")
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    verdicts = budget_verdicts(
        pack_rows=pack_rows, qpack_rows=qpack_rows, tpack_rows=tpack_rows
    )
    decision = decide_hbud(verdicts)
    write_json(
        out / "hbud_smoke.json",
        {
            "pack_rows": pack_rows,
            "qpack_rows": qpack_rows,
            "tpack_rows": tpack_rows,
            "verdicts": verdicts,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": PACK_CHUNK,
            "qpack_chunk": QPACK_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "delta_gflops_frac": DELTA_GFLOPS_FRAC,
            "mode": "hard wall+GFLOPs (ms/step) budget vs tip",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "hbud_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
