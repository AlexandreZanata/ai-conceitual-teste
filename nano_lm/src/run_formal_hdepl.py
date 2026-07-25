"""Formal H-DEPL: BUD survivors → deploy policy (fit≠eval)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from chunk_fit import long_prompts
from data_tiny import load_tokenizer
from depl_pair import (
    DELTA_GFLOPS_FRAC,
    LONG_TARGET_TOKENS,
    PACK_CHUNK,
    QPACK_CHUNK,
    SMOKE_BUDGETS,
    load_texts,
    run_depl_measure,
    tune_cpu_threads,
)
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hbud import formal_cfg as hbud_formal_cfg


def formal_cfg() -> dict[str, Any]:
    base = hbud_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hdepl"
    return base


def run_formal() -> int:
    threads = tune_cpu_threads()
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-DEPL formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        load_texts(c["prompts"], c["fit_prompts"]),
        tok,
        target_tokens=LONG_TARGET_TOKENS,
    )
    steps = int(c["steps_kd"])
    t0 = time.perf_counter()
    payload = run_depl_measure(
        c,
        out=out,
        device=device,
        vocab=len(tok),
        steps=steps,
        prompts=prompts,
        label_prefix="HDEPL_formal",
        pack_claim=9650,
        qpack_claim=9680,
    )
    payload.update(
        {
            "wall_s": time.perf_counter() - t0,
            "n_prompts": len(prompts),
            "chunk_size": PACK_CHUNK,
            "qpack_chunk": QPACK_CHUNK,
            "budgets": list(SMOKE_BUDGETS),
            "target_tokens": LONG_TARGET_TOKENS,
            "delta_gflops_frac": DELTA_GFLOPS_FRAC,
            "cpu_threads": threads,
            "steps": steps,
            "mode": "DEPL: BUD survivors → deploy policy (speed/quality/train)",
        }
    )
    write_json(out / "formal.json", payload)
    print(
        json.dumps({"decision": payload["decision"], "out": str(out / "formal.json")})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
