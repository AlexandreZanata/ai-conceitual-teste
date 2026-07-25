"""Formal H-QPACK: FLAYB vs POOL (eval, fit≠eval)."""

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
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from qpack_ops import QPACK_CHUNK
from qpack_pair import SMOKE_BUDGETS, run_seed_pair
from run_formal_hflayb import formal_cfg as hflayb_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hflayb_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hqpack"
    return base


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-QPACK formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    raw = _texts(c["prompts"]) + _texts(c["fit_prompts"])
    prompts = long_prompts(raw, tok, target_tokens=LONG_TARGET_TOKENS)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(run_seed_pair(c, seed, prompts, claim_offset=9944))
        torch.cuda.empty_cache()
    write_json(
        out / "formal.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": QPACK_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "mode": "FLAYB quality pack vs serial POOL",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
