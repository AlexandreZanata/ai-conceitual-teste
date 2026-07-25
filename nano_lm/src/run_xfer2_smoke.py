"""Smoke H-XFER2: PACK (+ optional BPACK) on elongated/ood/ood_long."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from bpack_pair import run_seed_trio as run_bpack_trio
from data_tiny import load_tokenizer
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from pack_pair import run_seed_trio
from xfer_packs import OOD_PROMPTS
from xfer2_ops import XFER2_PACKS, decide_hxfer2
from xfer2_packs import build_xfer2_packs
from xfer2_score import verdicts_from_rows

_CLAIM = {"elongated": 9700, "ood": 9710, "ood_long": 9720}


def _run_packs(
    c: dict[str, Any],
    packs: dict[str, dict[str, Any]],
    device,
) -> tuple[dict[str, list], dict[str, list]]:
    pack_by: dict[str, list] = {p: [] for p in XFER2_PACKS}
    bpack_by: dict[str, list] = {p: [] for p in XFER2_PACKS}
    for seed in c["seeds"]:
        for name in XFER2_PACKS:
            texts = packs[name]["texts"]
            print(json.dumps({"phase": "serve", "seed": seed, "pack": name}), flush=True)
            pack_by[name].extend(
                run_seed_trio(c, seed, texts, claim_offset=_CLAIM[name])
            )
            bpack_by[name].extend(
                run_bpack_trio(c, seed, texts, claim_offset=_CLAIM[name] + 30)
            )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return pack_by, bpack_by


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-XFER2 requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(OOD_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(OOD_PROMPTS))
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    packs = build_xfer2_packs(tok, harness=c["prompts"], fit=c["fit_prompts"])
    t0 = time.perf_counter()
    pack_by, bpack_by = _run_packs(c, packs, device)
    verdicts = verdicts_from_rows(pack_by=pack_by, bpack_by=bpack_by)
    decision = decide_hxfer2(verdicts)
    payload = {
        "pack_rows": pack_by,
        "bpack_rows": bpack_by,
        "verdicts": verdicts,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "packs": {
            n: {"n_prompts": p["n_prompts"], "target_tokens": p["target_tokens"]}
            for n, p in packs.items()
        },
        "mode": "transfer PACK (+BPACK report) on elongated/ood/ood_long",
    }
    write_json(out / "xfer2_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "xfer2_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
