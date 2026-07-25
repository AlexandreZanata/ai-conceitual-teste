"""Smoke H-PARETO: audit formal util pairs for GFLOPs-inflated tok/s wins."""

from __future__ import annotations

import json
import time

from matrix_common import REPO, write_json
from pareto_ops import DELTA_GFLOPS_FRAC, decide_hpareto
from pareto_scan import scan_formal_pairs


def main() -> int:
    t0 = time.perf_counter()
    pairs = scan_formal_pairs()
    n_flag = sum(1 for p in pairs if p["flagged"])
    decision = decide_hpareto(n_pairs=len(pairs), n_flagged=n_flag)
    out = REPO / "results/nano-lm/student-matrix/pareto_smoke.json"
    write_json(
        out,
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
    print(json.dumps({"n_pairs": len(pairs), "n_flagged": n_flag, "out": str(out)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
