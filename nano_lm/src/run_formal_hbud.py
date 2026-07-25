"""Formal H-BUD: hard wall/GFLOPs budgets vs tip (fit≠eval)."""

from __future__ import annotations

import json
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
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from pack_ops import PACK_CHUNK
from pack_pair import SMOKE_BUDGETS, run_seed_trio
from qpack_ops import QPACK_CHUNK
from qpack_pair import run_seed_pair as run_qpack_pair
from run_formal_hpack import formal_cfg as hpack_formal_cfg
from tpack_pair import run_seed_pair as run_tpack_pair


def formal_cfg() -> dict[str, Any]:
    base = hpack_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hbud"
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
        raise RuntimeError("H-BUD formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        _texts(c["prompts"]) + _texts(c["fit_prompts"]),
        tok,
        target_tokens=LONG_TARGET_TOKENS,
    )
    t0 = time.perf_counter()
    pack_rows: list[dict[str, Any]] = []
    qpack_rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "serve", "seed": seed}), flush=True)
        pack_rows.extend(run_seed_trio(c, seed, prompts, claim_offset=9550))
        qpack_rows.extend(run_qpack_pair(c, seed, prompts, claim_offset=9580))
        torch.cuda.empty_cache()
    steps = int(c["steps_kd"])
    vocab = len(tok)
    tpack_rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "tpack", "seed": seed}), flush=True)
        tpack_rows.extend(
            run_tpack_pair(
                c, out, seed, device, vocab, steps, label_prefix="HBUD_formal"
            )
        )
        torch.cuda.empty_cache()
    verdicts = budget_verdicts(
        pack_rows=pack_rows, qpack_rows=qpack_rows, tpack_rows=tpack_rows
    )
    decision = decide_hbud(verdicts)
    write_json(
        out / "formal.json",
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
            "steps": steps,
            "delta_gflops_frac": DELTA_GFLOPS_FRAC,
            "mode": "hard wall+GFLOPs (ms/step) budget vs tip",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
