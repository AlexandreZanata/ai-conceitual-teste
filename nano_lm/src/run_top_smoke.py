"""Smoke H-TOP: top-k soft-label cache vs live STAG (train step time)."""

from __future__ import annotations

import json
import sys
import time

import torch

from data_tiny import load_tokenizer
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from stag_ops import STAG_SEQ_LO
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES, run_seed_pair


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c.get("steps_cur", c["steps_kd"]))
    vocab = len(load_tokenizer(c["tokenizer_id"], c["cache"]))
    t0 = time.perf_counter()
    rows: list = []
    for seed in c["seeds"]:
        rows.extend(run_seed_pair(c, out, seed, device, vocab, steps))
    write_json(
        out / "top_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k": DEFAULT_TOP_K,
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "top_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
