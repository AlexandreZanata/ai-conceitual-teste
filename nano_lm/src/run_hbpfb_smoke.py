"""Smoke H-ABS-BPFB: PFB K=2 on bitcoin pack; wall↓ vs k=4."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from bpfb_ops import decide_hbpfb
from btc_packs import BTC_PROMPTS, build_btc_pack
from data_tiny import load_tokenizer
from dom_packs import DOM_PROMPTS
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from pfb2_ops import K2_BEAMS
from pfb_ops import K_BEAMS, PFB_TEMP
from pfb_score import (
    arm_means,
    attach_code_teacher,
    collect_beam_banks,
    collect_pfb_banks,
    commit_pfb_rows,
)
from prog_packs import PROG_PROMPTS
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10009
_MAX_NEW = 32
_PROXY = ("http_proxy", "https_proxy", "HTTP_PROXY", "HTTPS_PROXY", "ALL_PROXY", "all_proxy")


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return {**gene, "n": 1, "temperature": 1e-6}


def _free_cuda(*objs: object) -> None:
    for obj in objs:
        del obj
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def _identical(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> bool:
    return len(a) == len(b) and all(
        str(x["continuation"]) == str(y["continuation"]) for x, y in zip(a, b)
    )


def main() -> int:
    for key in _PROXY:
        os.environ.pop(key, None)
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-ABS-BPFB requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(DOM_PROMPTS), load_prompt_ids(BTC_PROMPTS))
    assert_disjoint(load_prompt_ids(PROG_PROMPTS), load_prompt_ids(BTC_PROMPTS))
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_btc_pack(tok)
    texts = pack["texts"]
    meta = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks4: list[dict[str, Any]] = []
    banks2: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "decode_btc", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(out, seed)
        claim = seed + _CLAIM
        p_part, b4 = collect_pfb_banks(
            story_teacher=story,
            student=student,
            prompts=texts,
            gene=gene,
            max_new=_MAX_NEW,
            seed=claim,
            k=K_BEAMS,
            temperature=PFB_TEMP,
            parent_family="H-EARLY-BTC",
        )
        b2 = collect_beam_banks(
            story_teacher=story,
            student=student,
            parent_rows=p_part,
            gene=gene,
            max_new=_MAX_NEW,
            beam_seed=claim + 2000,
            k=K2_BEAMS,
            temperature=PFB_TEMP,
        )
        parent_rows.extend(p_part)
        banks4.extend(b4)
        banks2.extend(b2)
        _free_cuda(story, student)
    print(json.dumps({"phase": "code_commit", "teacher": meta["hf_id"]}), flush=True)
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    parent_rows = attach_code_teacher(code, parent_rows)
    parent_code = {
        (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
        for r in parent_rows
    }
    bpfb4_rows = commit_pfb_rows(
        code, banks4, parent_code_by_key=parent_code, family="H-ABS-BPFB4"
    )
    bpfb2_rows = commit_pfb_rows(
        code, banks2, parent_code_by_key=parent_code, family="H-ABS-BPFB"
    )
    _free_cuda(code)
    parent_m, bpfb4_m, bpfb2_m = (
        arm_means(parent_rows),
        arm_means(bpfb4_rows),
        arm_means(bpfb2_rows),
    )
    decision = decide_hbpfb(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        bpfb_story=float(bpfb2_m["mean_story_lp"]),
        bpfb_code=float(bpfb2_m["mean_code_lp"]),
        mean_unique=float(bpfb2_m["mean_unique"]),
        mean_elig=float(bpfb2_m["mean_elig"]),
        mean_switch=float(bpfb2_m["mean_switch"]),
        bpfb_wall=float(bpfb2_m["mean_wall_ms"]),
        bpfb4_wall=float(bpfb4_m["mean_wall_ms"]),
        identical=_identical(parent_rows, bpfb2_rows),
    )
    payload = {
        "rows_parent": parent_rows,
        "rows_bpfb4": bpfb4_rows,
        "rows_bpfb2": bpfb2_rows,
        "parent_means": parent_m,
        "bpfb4_means": bpfb4_m,
        "bpfb2_means": bpfb2_m,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "pack": {k: pack[k] for k in ("name", "n_prompts", "target_tokens", "source")},
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "k2": K2_BEAMS,
        "k4": K_BEAMS,
        "pfb_temp": PFB_TEMP,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "BPFB: PFB K=2 on BTC@128 vs EARLY; wall↓ vs k=4",
        "mechanism": "PFB commit K=2 on bitcoin pack; domain-transfer gate",
        "parent": "H-EARLY n=1 greedy on B2 (BTC pack)",
    }
    write_json(out / "hbpfb_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "hbpfb_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
