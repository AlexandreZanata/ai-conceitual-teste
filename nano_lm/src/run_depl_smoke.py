"""Smoke H-DEPL: BUD survivors → runnable deploy policy gate."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

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
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json


def main() -> int:
    threads = tune_cpu_threads()
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-DEPL requires CUDA", file=sys.stderr)
        return 2
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    prompts = long_prompts(
        load_texts(c["prompts"], c["fit_prompts"]),
        tok,
        target_tokens=LONG_TARGET_TOKENS,
    )
    steps = int(c.get("steps_cur", c["steps_kd"]))
    t0 = time.perf_counter()
    payload = run_depl_measure(
        c,
        out=out,
        device=device,
        vocab=len(tok),
        steps=steps,
        prompts=prompts,
        label_prefix="HDEPL",
        pack_claim=9600,
        qpack_claim=9630,
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
    write_json(out / "hdepl_smoke.json", payload)
    print(
        json.dumps({"decision": payload["decision"], "out": str(out / "hdepl_smoke.json")})
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
