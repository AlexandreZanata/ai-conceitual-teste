"""Smoke H-DEPTHA: DEPTH student under ADAMF vs full ADAMF."""

from __future__ import annotations

import json
import sys
import time

from data_tiny import load_tokenizer
from deptha_pair import run_seed_pair
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from stag_ops import STAG_SEQ_LO
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-DEPTHA requires CUDA", file=sys.stderr)
        return 2
    out = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c.get("steps_cur", c["steps_kd"]))
    vocab = len(load_tokenizer(c["tokenizer_id"], c["cache"]))
    t0 = time.perf_counter()
    rows: list = []
    for seed in c["seeds"]:
        rows.extend(run_seed_pair(c, out, seed, device, vocab, steps))
    write_json(
        out / "deptha_smoke.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k": DEFAULT_TOP_K,
            "mode": "DEPTH student + ADAMF I/O vs full ADAMF",
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "deptha_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
