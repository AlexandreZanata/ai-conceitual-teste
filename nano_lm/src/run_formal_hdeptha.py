"""Formal H-DEPTHA: DEPTH under ADAMF vs H-ADAMF (formal KD budget)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from deptha_pair import run_seed_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hadamf import formal_cfg as hadamf_formal_cfg
from stag_ops import STAG_SEQ_LO
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES


def formal_cfg() -> dict[str, Any]:
    base = hadamf_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hdeptha"
    return base


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-DEPTHA formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c["steps_kd"])
    vocab = len(load_tokenizer(c["tokenizer_id"], c["cache"]))
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(
            run_seed_pair(
                c, out, seed, device, vocab, steps, label_prefix="HDEPTHA_formal"
            )
        )
        torch.cuda.empty_cache()
    write_json(
        out / "formal.json",
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
    print(json.dumps({"n_rows": len(rows), "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
