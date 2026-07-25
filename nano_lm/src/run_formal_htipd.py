"""Formal H-TIPD: tip decision RETIP→STAG′ xor util (fit≠eval)."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

from data_tiny import load_tokenizer
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import REPO, write_json
from run_formal_hretip import formal_cfg as hretip_formal_cfg
from stag_ops import STAG_SEQ_LO
from tipd_pair import load_texts, run_tipd_seeds, tune_cpu_threads
from top_ops import DEFAULT_TOP_K
from top_pair import TIP_STAGES


def formal_cfg() -> dict[str, Any]:
    base = hretip_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-htipd"
    return base


def run_formal() -> int:
    threads = tune_cpu_threads()
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-TIPD formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    early_dir = Path(c["early_dir"])
    pool_dir = Path(c["pool_dir"])
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    steps = int(c["steps_kd"])
    prompts = load_texts(c["prompts"])
    max_new = int(c.get("max_new_eval", 48))
    t0 = time.perf_counter()
    payload = run_tipd_seeds(
        c,
        out=out,
        device=device,
        vocab=len(tok),
        steps=steps,
        prompts=prompts,
        max_new=max_new,
        early_dir=early_dir,
        pool_dir=pool_dir,
        label_prefix="HTIPD_formal",
        claim_base=8100,
        pool_eval_fallback=False,
    )
    payload.update(
        {
            "wall_s": time.perf_counter() - t0,
            "seq_lo": STAG_SEQ_LO,
            "n_stages": TIP_STAGES,
            "steps": steps,
            "top_k": DEFAULT_TOP_K,
            "max_new": max_new,
            "n_prompts": len(prompts),
            "cpu_threads": threads,
            "mode": "TIPD: RETIP→STAG′ xor util (capacity + no serve regress)",
        }
    )
    write_json(out / "formal.json", payload)
    print(
        json.dumps(
            {
                "decision": payload["decision"],
                "tip_outcome": payload["tip_outcome"],
                "out": str(out / "formal.json"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
