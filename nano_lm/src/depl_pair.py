"""Shared H-DEPL measure: BUD survivors + deploy policy routes."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import torch
import yaml

from bud_ops import DELTA_GFLOPS_FRAC
from bud_score import budget_verdicts
from chunk_fit import long_prompts
from chunk_ops import LONG_TARGET_TOKENS
from depl_ops import DEPL_SCENARIOS, choose_recipe, decide_hdepl
from pack_ops import PACK_CHUNK
from pack_pair import SMOKE_BUDGETS, run_seed_trio
from qpack_ops import QPACK_CHUNK
from qpack_pair import run_seed_pair as run_qpack_pair
from tipd_pair import tune_cpu_threads
from tpack_pair import run_seed_pair as run_tpack_pair

__all__ = [
    "DELTA_GFLOPS_FRAC",
    "LONG_TARGET_TOKENS",
    "PACK_CHUNK",
    "QPACK_CHUNK",
    "SMOKE_BUDGETS",
    "load_texts",
    "policy_routes",
    "run_depl_measure",
    "tune_cpu_threads",
]


def load_texts(*paths: Path) -> list[str]:
    out: list[str] = []
    for path in paths:
        with path.open(encoding="utf-8") as f:
            out.extend(p["text"] for p in yaml.safe_load(f)["prompts"])
    return out


def policy_routes() -> list[dict[str, str]]:
    """Materialize canonical scenario → choice rows for reports."""
    rows: list[dict[str, str]] = []
    for sc in DEPL_SCENARIOS:
        choice = choose_recipe(
            goal=str(sc["goal"]),
            in_dist=bool(sc["in_dist"]),
            ood_long=bool(sc["ood_long"]),
        )
        rows.append(
            {
                "id": str(sc["id"]),
                "goal": str(sc["goal"]),
                "in_dist": str(bool(sc["in_dist"])),
                "ood_long": str(bool(sc["ood_long"])),
                "choice": choice,
            }
        )
    return rows


def run_depl_measure(
    c: dict[str, Any],
    *,
    out: Path,
    device,
    vocab: int,
    steps: int,
    prompts: list[str],
    label_prefix: str,
    pack_claim: int,
    qpack_claim: int,
) -> dict[str, Any]:
    """
    GIVEN matrix cfg + elongated prompts
    WHEN scoring PACK/QPACK/TPACK under BUD then applying DEPL policy
    THEN return rows, verdicts, routes, and decide_hdepl.
    """
    pack_rows: list[dict[str, Any]] = []
    qpack_rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "serve", "seed": seed}), flush=True)
        pack_rows.extend(run_seed_trio(c, seed, prompts, claim_offset=pack_claim))
        qpack_rows.extend(
            run_qpack_pair(c, seed, prompts, claim_offset=qpack_claim)
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    tpack_rows: list[dict[str, Any]] = []
    for seed in c["seeds"]:
        print(json.dumps({"phase": "tpack", "seed": seed}), flush=True)
        tpack_rows.extend(
            run_tpack_pair(
                c, out, seed, device, vocab, steps, label_prefix=label_prefix
            )
        )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    verdicts = budget_verdicts(
        pack_rows=pack_rows, qpack_rows=qpack_rows, tpack_rows=tpack_rows
    )
    routes = policy_routes()
    decision = decide_hdepl(verdicts)
    return {
        "pack_rows": pack_rows,
        "qpack_rows": qpack_rows,
        "tpack_rows": tpack_rows,
        "bud_verdicts": verdicts,
        "routes": routes,
        "decision": decision,
    }
