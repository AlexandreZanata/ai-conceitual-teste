"""Formal H-EFF: PACK efficiency re-measure (fit≠eval genes)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any, Callable

import torch

from btc_packs import build_btc_pack
from data_tiny import load_tokenizer
from eff_ops import PHASE_B_SERVE, decide_heff
from eff_score import means_by_domain
from load_model import resolve_device
from matrix_common import REPO, write_json
from pack_pair import run_seed_trio
from prog_packs import build_prog_pack
from run_eff_smoke import _assert_holdouts
from run_formal_hpack import formal_cfg as hpack_formal_cfg
from tipd_pair import tune_cpu_threads

_CLAIM = 9880


def formal_cfg() -> dict[str, Any]:
    base = hpack_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-heff"
    return base


def _measure(
    c: dict[str, Any],
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
        torch.cuda.empty_cache()
    meta = {
        "name": pack["name"],
        "n_prompts": pack["n_prompts"],
        "target_tokens": pack["target_tokens"],
        "source": pack["source"],
    }
    return meta, rows


def run_formal() -> int:
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = formal_cfg()
    _assert_holdouts(c)
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-EFF formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    t0 = time.perf_counter()
    domain_rows: dict[str, list[dict[str, Any]]] = {}
    packs: dict[str, Any] = {}
    for name, builder, claim in (
        ("prog", build_prog_pack, _CLAIM),
        ("btc", build_btc_pack, _CLAIM + 10),
    ):
        meta, rows = _measure(c, tok, name=name, builder=builder, claim=claim)
        packs[name] = meta
        domain_rows[name] = rows
    means = means_by_domain(domain_rows)
    decision = decide_heff(means)
    write_json(
        out / "formal.json",
        {
            "domain_rows": domain_rows,
            "means": means,
            "baselines": PHASE_B_SERVE,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "packs": packs,
            "cpu_threads": threads,
            "mode": (
                "EFF formal: PACK re-measure prog+btc @128 vs Phase B SERVE; "
                "fit≠eval genes"
            ),
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
