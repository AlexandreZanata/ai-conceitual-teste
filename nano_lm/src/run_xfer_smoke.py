"""Smoke H-XFER: re-eval PACK/QPACK/TPACK on heldout/elongated/ood packs."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from pack_pair import run_seed_trio
from qpack_pair import run_seed_pair as run_qpack_pair
from tpack_pair import eval_seed_rows, train_seed_pair
from xfer_ops import XFER_PACKS, decide_hxfer
from xfer_packs import OOD_PROMPTS, build_xfer_packs, write_texts_yaml
from xfer_score import verdicts_from_rows

_CLAIM = {"heldout": 9600, "elongated": 9610, "ood": 9620}


def _run_serve(
    c: dict[str, Any],
    packs: dict[str, dict[str, Any]],
    device,
) -> tuple[dict[str, list], dict[str, list]]:
    pack_by: dict[str, list] = {p: [] for p in XFER_PACKS}
    qpack_by: dict[str, list] = {p: [] for p in XFER_PACKS}
    for seed in c["seeds"]:
        for name in XFER_PACKS:
            texts = packs[name]["texts"]
            print(json.dumps({"phase": "serve", "seed": seed, "pack": name}), flush=True)
            pack_by[name].extend(
                run_seed_trio(c, seed, texts, claim_offset=_CLAIM[name])
            )
            qpack_by[name].extend(
                run_qpack_pair(c, seed, texts, claim_offset=_CLAIM[name] + 30)
            )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return pack_by, qpack_by


def _run_tpack(
    c: dict[str, Any],
    out: Path,
    device,
    vocab: int,
    steps: int,
    yaml_by: dict[str, Path],
) -> dict[str, list]:
    tpack_by: dict[str, list] = {p: [] for p in XFER_PACKS}
    for seed in c["seeds"]:
        print(json.dumps({"phase": "tpack_train", "seed": seed}), flush=True)
        live, tpack = train_seed_pair(
            c, out, seed, device, vocab, steps, label_prefix="HXFER"
        )
        for name in XFER_PACKS:
            print(json.dumps({"phase": "tpack_eval", "seed": seed, "pack": name}), flush=True)
            tpack_by[name].extend(
                eval_seed_rows(
                    c,
                    live,
                    tpack,
                    seed,
                    label_prefix="HXFER",
                    prompts_path=yaml_by[name],
                    pack_tag=name,
                )
            )
        if device.type == "cuda":
            torch.cuda.empty_cache()
    return tpack_by


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-XFER requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(OOD_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(OOD_PROMPTS))
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    c["gene_dir"] = out
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    packs = build_xfer_packs(tok, harness=c["prompts"], fit=c["fit_prompts"])
    yaml_by = {
        name: write_texts_yaml(
            out / f"xfer_{name}_prompts.yaml",
            packs[name]["texts"],
            id_prefix=f"t{name[0]}",
        )
        for name in XFER_PACKS
    }
    t0 = time.perf_counter()
    pack_by, qpack_by = _run_serve(c, packs, device)
    write_json(
        out / "xfer_smoke_serve.json",
        {"pack_rows": pack_by, "qpack_rows": qpack_by, "wall_s": time.perf_counter() - t0},
    )
    steps = int(c.get("steps_cur", c["steps_kd"]))
    vocab = len(tok)
    tpack_by = _run_tpack(c, out, device, vocab, steps, yaml_by)
    verdicts = verdicts_from_rows(
        pack_by=pack_by, qpack_by=qpack_by, tpack_by=tpack_by
    )
    decision = decide_hxfer(verdicts)
    payload = {
        "pack_rows": pack_by,
        "qpack_rows": qpack_by,
        "tpack_rows": tpack_by,
        "verdicts": verdicts,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "packs": {
            n: {"n_prompts": p["n_prompts"], "target_tokens": p["target_tokens"]}
            for n, p in packs.items()
        },
        "mode": "transfer PACK/QPACK/TPACK on heldout/elongated/ood",
    }
    write_json(out / "xfer_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "xfer_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
