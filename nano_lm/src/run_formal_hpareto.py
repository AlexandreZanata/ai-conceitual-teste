"""Formal H-PARETO: same formal-corpus audit (instrumentation gate)."""

from __future__ import annotations

import json
import time
from pathlib import Path

from matrix_common import REPO, write_json
from pareto_ops import DELTA_GFLOPS_FRAC, decide_hpareto
from pareto_scan import scan_formal_pairs


def formal_cfg() -> dict:
    return {"out": REPO / "results/nano-lm/formal-hpareto"}


def run_formal() -> int:
    c = formal_cfg()
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    t0 = time.perf_counter()
    pairs = scan_formal_pairs()
    n_flag = sum(1 for p in pairs if p["flagged"])
    decision = decide_hpareto(n_pairs=len(pairs), n_flagged=n_flag)
    write_json(
        out / "formal.json",
        {
            "pairs": pairs,
            "n_pairs": len(pairs),
            "n_flagged": n_flag,
            "delta_frac": DELTA_GFLOPS_FRAC,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "mode": "formal-corpus efficiency audit (report-only)",
        },
    )
    print(
        json.dumps(
            {
                "n_pairs": len(pairs),
                "n_flagged": n_flag,
                "out": str(out / "formal.json"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
