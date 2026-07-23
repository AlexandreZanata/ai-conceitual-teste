"""Orchestrate student-matrix smoke: baselines + hyps + quantum ablation."""

from __future__ import annotations

import json
import sys
import time
from typing import Any

from load_model import resolve_device
from matrix_baselines import run_baselines
from matrix_common import matrix_cfg, write_json
from matrix_decode import run_decode_ops
from matrix_hyps import run_hypotheses
from matrix_quantum import run_quantum


def run_matrix() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; matrix will be slow/CPU", file=sys.stderr)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    run_baselines(c, device, rows)
    run_decode_ops(c, rows)
    run_hypotheses(c, device, rows)
    run_quantum(c, rows)
    payload = {
        "rows": rows,
        "wall_s": time.perf_counter() - t0,
        "config": {
            k: str(v) if hasattr(v, "name") else v for k, v in c.items()
        },
    }
    write_json(c["out"] / "matrix.json", payload)
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "matrix.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_matrix())
