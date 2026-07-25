"""Smoke H-AMORT: cache once, N PRE3 runs; amortized e2e vs live STAG."""

from __future__ import annotations

import json
import sys
import time

from amort_ops import DEFAULT_N_RUNS, amortized_e2e, decide_hamort
from amort_pair import run_amort_seed
from data_tiny import load_tokenizer
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from stag_ops import STAG_SEQ_LO
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES


def _means(vals: list[float]) -> float:
    return sum(vals) / max(len(vals), 1)


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-AMORT requires CUDA", file=sys.stderr)
        return 2
    out = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c.get("steps_cur", c["steps_kd"]))
    vocab = len(load_tokenizer(c["tokenizer_id"], c["cache"]))
    n_runs = int(c.get("amort_n_runs", DEFAULT_N_RUNS))
    t0 = time.perf_counter()
    seed_rows: list[dict] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "amort", "seed": seed, "n_runs": n_runs}), flush=True)
        seed_rows.append(
            run_amort_seed(
                c, out, seed, device, vocab, steps, n_runs, label_prefix="HAMORT"
            )
        )
    live_lps = [float(r["live_lp"]) for r in seed_rows]
    live_walls = [float(r["live_train_wall_s"]) for r in seed_rows]
    amort_lps: list[float] = []
    amort_e2es: list[float] = []
    for r in seed_rows:
        amort_lps.append(_means(r["pre3_lps"]))
        amort_e2es.append(amortized_e2e(r["cache_build_s"], r["pre3_train_walls"]))
    live_lp = _means(live_lps)
    live_e2e = _means(live_walls)
    amort_lp = _means(amort_lps)
    amort_e2e_m = _means(amort_e2es)
    decision = decide_hamort(
        amort_e2e=amort_e2e_m,
        live_e2e=live_e2e,
        amort_lp=amort_lp,
        live_lp=live_lp,
        n_runs=n_runs,
    )
    write_json(
        out / "amort_smoke.json",
        {
            "seed_rows": seed_rows,
            "mean_live_lp": live_lp,
            "mean_live_e2e": live_e2e,
            "mean_amort_lp": amort_lp,
            "mean_amort_e2e": amort_e2e_m,
            "n_runs": n_runs,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k": DEFAULT_TOP_K,
            "mode": f"cache once + n={n_runs} PRE3; amortized e2e vs live STAG",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "amort_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
