"""Formal H-TOPK: smoke-best k vs tip k=64 (formal KD budget)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import ROOT, REPO, write_json
from run_formal_hcurl import formal_cfg as hcurl_formal_cfg
from stag_ops import STAG_SEQ_LO
from top_pair import TIP_STAGES
from topk_ops import SMOKE_BEST_K, TIP_TOP_K
from topk_pair import run_seed_ks


def formal_cfg() -> dict[str, Any]:
    base = hcurl_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-htopk"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    base["prompts"] = ROOT / "prompts/eval_prompts.yaml"
    return base


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    steps = int(c["steps_kd"])
    vocab = len(load_tokenizer(c["tokenizer_id"], c["cache"]))
    ks = (int(SMOKE_BEST_K), int(TIP_TOP_K))
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(
            run_seed_ks(
                c,
                out,
                seed,
                device,
                vocab,
                steps,
                ks=ks,
                label_prefix="HTOPK_formal",
            )
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    write_json(
        out / "formal.json",
        {
            "rows": rows,
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k_sweep": list(ks),
            "tip_top_k": TIP_TOP_K,
            "challenger_k": SMOKE_BEST_K,
        },
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
