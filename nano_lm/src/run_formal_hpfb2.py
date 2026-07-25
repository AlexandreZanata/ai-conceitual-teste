"""Formal H-ABS-PFB2: K=2 PFB vs EARLY; wall↓ vs PFB k=4 (fit≠eval)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from dom_packs import DOM_PROMPTS
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, write_json
from pfb2_ops import K2_BEAMS, decide_hpfb2
from pfb_ops import K_BEAMS, PFB_TEMP
from pfb_score import (
    arm_means,
    attach_code_teacher,
    collect_beam_banks,
    collect_pfb_banks,
    commit_pfb_rows,
)
from prog_packs import PROG_PROMPTS, build_prog_pack
from run_formal_hprog import formal_cfg as hprog_formal_cfg
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10003
_MAX_NEW = 32


def formal_cfg() -> dict[str, Any]:
    base = hprog_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hpfb2"
    return base


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
    if len(a) != len(b):
        return False
    return all(
        str(x["continuation"]) == str(y["continuation"]) for x, y in zip(a, b)
    )


def run_formal() -> int:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(DOM_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-ABS-PFB2 formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    early_dir = Path(c["early_dir"])
    ckpt_dir = Path(c["ckpt_dir"])
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok)
    texts = pack["texts"]
    meta = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks4: list[dict[str, Any]] = []
    banks2: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "decode", "seed": seed}), flush=True)
        ckpt = ckpt_dir / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(early_dir, seed)
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
    pfb4_rows = commit_pfb_rows(
        code, banks4, parent_code_by_key=parent_code, family="H-ABS-PFB"
    )
    pfb2_rows = commit_pfb_rows(
        code, banks2, parent_code_by_key=parent_code, family="H-ABS-PFB2"
    )
    _free_cuda(code)
    parent_m = arm_means(parent_rows)
    pfb4_m = arm_means(pfb4_rows)
    pfb2_m = arm_means(pfb2_rows)
    decision = decide_hpfb2(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        pfb2_story=float(pfb2_m["mean_story_lp"]),
        pfb2_code=float(pfb2_m["mean_code_lp"]),
        mean_unique=float(pfb2_m["mean_unique"]),
        mean_elig=float(pfb2_m["mean_elig"]),
        mean_switch=float(pfb2_m["mean_switch"]),
        pfb2_wall=float(pfb2_m["mean_wall_ms"]),
        pfb4_wall=float(pfb4_m["mean_wall_ms"]),
        identical=_identical(parent_rows, pfb2_rows),
    )
    write_json(
        out / "formal.json",
        {
            "rows_parent": parent_rows,
            "rows_pfb4": pfb4_rows,
            "rows_pfb2": pfb2_rows,
            "parent_means": parent_m,
            "pfb4_means": pfb4_m,
            "pfb2_means": pfb2_m,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "pack": {
                "name": pack["name"],
                "n_prompts": pack["n_prompts"],
                "target_tokens": pack["target_tokens"],
                "source": pack["source"],
            },
            "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
            "code_teacher": meta,
            "k2": K2_BEAMS,
            "k4": K_BEAMS,
            "pfb_temp": PFB_TEMP,
            "max_new": _MAX_NEW,
            "cpu_threads": threads,
            "mode": "PFB2 formal: K=2 vs EARLY; wall↓ vs PFB k=4 (fit≠eval)",
            "mechanism": "PFB commit K=2; efficiency gate vs PFB k=4",
            "parent": "H-EARLY n=1 greedy on B2 (formal genes)",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
