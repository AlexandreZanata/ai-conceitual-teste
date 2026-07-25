"""Formal H-DOM: PACK tip gate on howto domain (fit≠eval genes; domain eval)."""

from __future__ import annotations

import json
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
from matrix_common import REPO, write_json
from pack_pair import run_seed_trio
from run_formal_hpack import formal_cfg as hpack_formal_cfg
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 9850


def formal_cfg() -> dict[str, Any]:
    base = hpack_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hdom"
    return base


def run_formal() -> int:
    threads = tune_cpu_threads()
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(DOM_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(DOM_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(DOM_PROMPTS))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-DOM formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_dom_pack(tok)
    texts = pack["texts"]
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "serve", "seed": seed, "pack": pack["name"]}), flush=True)
        rows.extend(run_seed_trio(c, seed, texts, claim_offset=_CLAIM))
        torch.cuda.empty_cache()
    verdicts = verdicts_from_rows(rows)
    decision = decide_hdom(verdicts)
    write_json(
        out / "formal.json",
        {
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
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
