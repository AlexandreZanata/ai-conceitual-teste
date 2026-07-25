"""Smoke H-TCACHE: memo + eligible-only code score on PFB2; forwards↓≥30%."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from dom_packs import DOM_PROMPTS
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import matrix_cfg, write_json
from pfb2_ops import K2_BEAMS
from pfb_ops import PFB_TEMP
from pfb_score import arm_means, attach_code_teacher, collect_beam_banks, collect_pfb_banks
from prog_packs import PROG_PROMPTS, build_prog_pack
from tcache_ops import TeacherLpMemo, decide_htcache
from tcache_score import (
    commit_pfb_rows_naive,
    commit_pfb_rows_tcache,
    rescore_bank_stories,
)
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10021
_MAX_NEW = 32
_PROXY = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "all_proxy",
)


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
        print("ERROR: H-TCACHE requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(DOM_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok)
    texts = pack["texts"]
    meta = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks2: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "decode", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(out, seed)
        claim = seed + _CLAIM
        p_part, _ = collect_pfb_banks(
            story_teacher=story,
            student=student,
            prompts=texts,
            gene=gene,
            max_new=_MAX_NEW,
            seed=claim,
            k=1,
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
        banks2.extend(b2)
        _free_cuda(story, student)
    print(json.dumps({"phase": "score_compare", "teacher": meta["hf_id"]}), flush=True)
    # Reload story teacher for fair rescore arms (VRAM: free student already).
    story = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    naive_story_forwards = sum(len(b["conts"]) for b in banks2)
    banks_naive, story_wall_n = rescore_bank_stories(story, banks2, memo=None)
    tc_memo = TeacherLpMemo()
    banks_tc, story_wall_t = rescore_bank_stories(story, banks2, memo=tc_memo)
    _free_cuda(story)
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    parent_rows = attach_code_teacher(code, parent_rows)
    parent_code = {
        (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
        for r in parent_rows
    }
    naive_rows, naive_code_memo, code_wall_n = commit_pfb_rows_naive(
        code, banks_naive, parent_code_by_key=parent_code
    )
    tc_rows, tc_code_memo, code_wall_t = commit_pfb_rows_tcache(
        code, banks_tc, parent_code_by_key=parent_code, story_memo=tc_memo
    )
    _free_cuda(code)
    naive_forwards = float(naive_story_forwards + naive_code_memo.forwards)
    tcache_forwards = float(tc_memo.forwards)
    naive_wall = float(story_wall_n + code_wall_n)
    tcache_wall = float(story_wall_t + code_wall_t)
    parent_m, naive_m, tc_m = (
        arm_means(parent_rows),
        arm_means(naive_rows),
        arm_means(tc_rows),
    )
    decision = decide_htcache(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        tcache_story=float(tc_m["mean_story_lp"]),
        tcache_code=float(tc_m["mean_code_lp"]),
        mean_unique=float(tc_m["mean_unique"]),
        mean_elig=float(tc_m["mean_elig"]),
        mean_switch=float(tc_m["mean_switch"]),
        tcache_wall=tcache_wall,
        naive_wall=naive_wall,
        tcache_forwards=tcache_forwards,
        naive_forwards=naive_forwards,
        identical=_identical(parent_rows, tc_rows),
    )
    payload = {
        "rows_parent": parent_rows,
        "rows_naive": naive_rows,
        "rows_tcache": tc_rows,
        "parent_means": parent_m,
        "naive_means": naive_m,
        "tcache_means": tc_m,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "naive_forwards": naive_forwards,
        "tcache_forwards": tcache_forwards,
        "naive_score_wall_ms": naive_wall,
        "tcache_score_wall_ms": tcache_wall,
        "tcache_hit_rate": tc_memo.hit_rate(),
        "pack": {k: pack[k] for k in ("name", "n_prompts", "target_tokens", "source")},
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "k": K2_BEAMS,
        "pfb_temp": PFB_TEMP,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "TCACHE: memo + eligible-only code on PFB2 vs naive score",
        "mechanism": "TeacherLpMemo by completion id; code forwards only if story-eligible",
        "parent": "H-EARLY n=1 greedy on B2 (PFB2 recipe freeze)",
    }
    write_json(out / "htcache_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "htcache_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
