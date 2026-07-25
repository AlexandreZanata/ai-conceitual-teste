"""Smoke H-EFF: re-measure PACK wall/tok/s/GFLOPs on prog+btc vs Phase B."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any, Callable

import torch

from btc_packs import BTC_PROMPTS, build_btc_pack
from data_tiny import load_tokenizer
from dom_packs import DOM_PROMPTS
from eff_ops import PHASE_B_SERVE, decide_heff
from eff_score import means_by_domain
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from pack_pair import run_seed_trio
from prog_packs import PROG_PROMPTS, build_prog_pack
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 9780


def _assert_holdouts(c: dict[str, Any]) -> None:
    smoke = load_prompt_ids(c["prompts"])
    fit = load_prompt_ids(c["fit_prompts"])
    assert_disjoint(fit, smoke)
    for path in (PROG_PROMPTS, BTC_PROMPTS, DOM_PROMPTS, OOD_PROMPTS):
        ids = load_prompt_ids(path)
        assert_disjoint(smoke, ids)
        assert_disjoint(fit, ids)
    assert_disjoint(load_prompt_ids(PROG_PROMPTS), load_prompt_ids(BTC_PROMPTS))


def _measure_pack(
    c: dict[str, Any],
    device: torch.device,
    tok: object,
    *,
    name: str,
    builder: Callable[..., dict[str, Any]],
    claim: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    pack = builder(tok)
    rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(
            json.dumps({"phase": "serve", "seed": seed, "pack": name}),
            flush=True,
        )
        rows.extend(run_seed_trio(c, seed, pack["texts"], claim_offset=claim))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    meta = {
        "name": pack["name"],
        "n_prompts": pack["n_prompts"],
        "target_tokens": pack["target_tokens"],
        "source": pack["source"],
    }
    return meta, rows


def main() -> int:
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-EFF requires CUDA", file=sys.stderr)
        return 2
    _assert_holdouts(c)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    t0 = time.perf_counter()
    domain_rows: dict[str, list[dict[str, Any]]] = {}
    packs: dict[str, Any] = {}
    meta, rows = _measure_pack(
        c, device, tok, name="prog", builder=build_prog_pack, claim=_CLAIM
    )
    packs["prog"] = meta
    domain_rows["prog"] = rows
    meta, rows = _measure_pack(
        c, device, tok, name="btc", builder=build_btc_pack, claim=_CLAIM + 10
    )
    packs["btc"] = meta
    domain_rows["btc"] = rows
    means = means_by_domain(domain_rows)
    decision = decide_heff(means)
    payload = {
        "domain_rows": domain_rows,
        "means": means,
        "baselines": PHASE_B_SERVE,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "packs": packs,
        "cpu_threads": threads,
        "mode": (
            "EFF smoke: PACK re-measure prog+btc @128 vs Phase B SERVE; "
            "TPACK/AMORT remain story-train-only (unchanged)"
        ),
    }
    write_json(out / "heff_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "heff_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
