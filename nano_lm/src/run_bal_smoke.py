"""Smoke H-BAL on matrix out dir; merge rows into matrix.json."""

from __future__ import annotations

import json
import sys
import time
from typing import Any

from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from matrix_hyps import _run_bal


def _merge_matrix(out_rows: list[dict[str, Any]], wall_s: float, c: dict) -> None:
    path = c["out"] / "matrix.json"
    if not path.is_file():
        write_json(path, {"rows": out_rows, "wall_s": wall_s})
        return
    data = json.loads(path.read_text(encoding="utf-8"))
    kept = [r for r in data.get("rows", []) if r.get("family") != "H-BAL"]
    data["rows"] = kept + out_rows
    data["bal_wall_s"] = wall_s
    write_json(path, data)


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    _run_bal(c, device, rows)
    wall_s = time.perf_counter() - t0
    write_json(c["out"] / "bal_smoke.json", {"rows": rows, "wall_s": wall_s})
    _merge_matrix(rows, wall_s, c)
    # also dump train wall from metas for compare note
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "bal_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
