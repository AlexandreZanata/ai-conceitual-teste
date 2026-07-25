"""Smoke H-DOM: PACK tip gate on new howto domain (≤5M + TinyStories teacher)."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from dom_ops import decide_hdom
from dom_packs import DOM_PROMPTS, build_dom_pack
from dom_score import verdicts_from_rows
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from pack_pair import run_seed_trio
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 9750


def main() -> int:
    threads = tune_cpu_threads()
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-DOM requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(DOM_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(DOM_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(DOM_PROMPTS))
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_dom_pack(tok)
    texts = pack["texts"]
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "serve", "seed": seed, "pack": pack["name"]}), flush=True)
        rows.extend(run_seed_trio(c, seed, texts, claim_offset=_CLAIM))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    verdicts = verdicts_from_rows(rows)
    decision = decide_hdom(verdicts)
    payload = {
        "pack_rows": rows,
        "verdicts": verdicts,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "pack": {
            "name": pack["name"],
            "n_prompts": pack["n_prompts"],
            "target_tokens": pack["target_tokens"],
            "source": pack["source"],
        },
        "cpu_threads": threads,
        "mode": "DOM: PACK tip gate on howto domain @128",
    }
    write_json(out / "hdom_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "hdom_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
