"""Smoke Phase E5: build heldout/frontier packs; serve frontier @128 on CUDA."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from btc_packs import BTC_PROMPTS
from chunk_fit import long_prompts
from data_tiny import load_tokenizer
from eval_suites import E5_BTC_HELDOUT, E5_PROG_HELDOUT, EVAL_SUITE_PATHS
from frontier_packs import build_frontier_pack
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from pack_pair import run_seed_trio
from prog_packs import PROG_PROMPTS
from tipd_pair import tune_cpu_threads
from xfer_packs import load_yaml_texts

_CLAIM = 9900


def _assert_suite_holdouts(c: dict[str, Any]) -> None:
    for path in EVAL_SUITE_PATHS:
        assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(path))
        assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(path))
        assert_disjoint(load_prompt_ids(PROG_PROMPTS), load_prompt_ids(path))
        assert_disjoint(load_prompt_ids(BTC_PROMPTS), load_prompt_ids(path))


def main() -> int:
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: Phase E5 smoke requires CUDA", file=sys.stderr)
        return 2
    _assert_suite_holdouts(c)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    frontier = build_frontier_pack(tok)
    heldout = {
        "prog": {
            "n": len(long_prompts(load_yaml_texts(E5_PROG_HELDOUT), tok)),
            "source": str(E5_PROG_HELDOUT),
        },
        "btc": {
            "n": len(long_prompts(load_yaml_texts(E5_BTC_HELDOUT), tok)),
            "source": str(E5_BTC_HELDOUT),
        },
    }
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"][:1]:
        print(json.dumps({"phase": "serve", "seed": seed, "pack": "frontier"}), flush=True)
        rows.extend(run_seed_trio(c, seed, frontier["texts"], claim_offset=_CLAIM))
        torch.cuda.empty_cache()
    payload = {
        "frontier": frontier,
        "heldout": heldout,
        "pack_rows": rows,
        "wall_s": time.perf_counter() - t0,
        "cpu_threads": threads,
        "mode": "E5 smoke: heldout YAML + frontier pack build; one-seed PACK serve",
        "ok": len(rows) >= 3,
    }
    write_json(out / "e5_smoke.json", payload)
    print(json.dumps({"ok": payload["ok"], "out": str(out / "e5_smoke.json"), "n_rows": len(rows)}))
    return 0 if payload["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
