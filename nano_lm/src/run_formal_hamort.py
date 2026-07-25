"""Formal H-AMORT: amortized soft-cache e2e vs live STAG (fit≠eval)."""

from __future__ import annotations

import json
import time
from typing import Any

from amort_ops import DEFAULT_N_RUNS, amortized_e2e, decide_hamort
from amort_pair import run_amort_seed
from data_tiny import load_tokenizer
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_htpack import formal_cfg as htpack_formal_cfg
from stag_ops import STAG_SEQ_LO
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES


def formal_cfg() -> dict[str, Any]:
    base = htpack_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hamort"
    base["amort_n_runs"] = DEFAULT_N_RUNS
    return base


def _means(vals: list[float]) -> float:
    return sum(vals) / max(len(vals), 1)


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-AMORT formal requires CUDA")
    out = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c["steps_kd"])
    vocab = len(load_tokenizer(c["tokenizer_id"], c["cache"]))
    n_runs = int(c.get("amort_n_runs", DEFAULT_N_RUNS))
    t0 = time.perf_counter()
    seed_rows: list[dict] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "amort", "seed": seed, "n_runs": n_runs}), flush=True)
        seed_rows.append(
            run_amort_seed(
                c,
                out,
                seed,
                device,
                vocab,
                steps,
                n_runs,
                label_prefix="HAMORT_formal",
            )
        )
    live_lp = _means([float(r["live_lp"]) for r in seed_rows])
    live_e2e = _means([float(r["live_train_wall_s"]) for r in seed_rows])
    amort_lps = [_means(r["pre3_lps"]) for r in seed_rows]
    amort_e2es = [
        amortized_e2e(r["cache_build_s"], r["pre3_train_walls"]) for r in seed_rows
    ]
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
        out / "formal.json",
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
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
