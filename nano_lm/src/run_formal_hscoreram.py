"""Formal H-SCORERAM: disk/RAM pack score cache (fit≠eval)."""

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
from pfb2_ops import K2_BEAMS
from pfb_ops import PFB_TEMP
from pfb_score import arm_means, attach_code_teacher, collect_beam_banks, collect_pfb_banks
from prog_packs import PROG_PROMPTS, build_prog_pack
from run_formal_hprog import formal_cfg as hprog_formal_cfg
from scoreram_ops import PackScoreCache, decide_hscoreram
from scoreram_score import score_pack_pass
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10033
_MAX_NEW = 32
_PROXY = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "all_proxy",
)


def formal_cfg() -> dict[str, Any]:
    base = hprog_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hscoreram"
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


def run_formal() -> int:
    for key in _PROXY:
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
        raise RuntimeError("H-SCORERAM formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    cache_path = out / "scoreram_pack_cache.json"
    early_dir = Path(c["early_dir"])
    ckpt_dir = Path(c["ckpt_dir"])
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok)
    texts = pack["texts"]
    meta = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
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
    print(json.dumps({"phase": "score_cold_warm", "teacher": meta["hf_id"]}), flush=True)
    story = load_causal_lm(
        c["teacher_id"], c["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    parent_rows = attach_code_teacher(code, parent_rows)
    parent_code = {
        (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
        for r in parent_rows
    }
    cold = PackScoreCache()
    cold_rows, cold_wall = score_pack_pass(
        story_teacher=story,
        code_teacher=code,
        banks=banks2,
        parent_code_by_key=parent_code,
        cache=cold,
    )
    cold.save(cache_path)
    warm = PackScoreCache.load(cache_path)
    warm_rows, warm_wall = score_pack_pass(
        story_teacher=story,
        code_teacher=code,
        banks=banks2,
        parent_code_by_key=parent_code,
        cache=warm,
    )
    _free_cuda(story, code)
    cold_m, warm_m = arm_means(cold_rows), arm_means(warm_rows)
    hit_rate = warm.hit_rate()
    decision = decide_hscoreram(
        cold_wall=cold_wall,
        warm_wall=warm_wall,
        cold_story=float(cold_m["mean_story_lp"]),
        warm_story=float(warm_m["mean_story_lp"]),
        cold_code=float(cold_m["mean_code_lp"]),
        warm_code=float(warm_m["mean_code_lp"]),
        hit_rate=hit_rate,
    )
    write_json(
        out / "formal.json",
        {
            "rows_cold": cold_rows,
            "rows_warm": warm_rows,
            "cold_means": cold_m,
            "warm_means": warm_m,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "cold_score_wall_ms": cold_wall,
            "warm_score_wall_ms": warm_wall,
            "cold_forwards": float(cold.forwards),
            "warm_forwards": float(warm.forwards),
            "warm_hit_rate": hit_rate,
            "cache_entries": cold.size(),
            "cache_path": str(cache_path),
            "pack": {
                k: pack[k] for k in ("name", "n_prompts", "target_tokens", "source")
            },
            "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
            "code_teacher": meta,
            "k": K2_BEAMS,
            "pfb_temp": PFB_TEMP,
            "max_new": _MAX_NEW,
            "cpu_threads": threads,
            "mode": "SCORERAM formal: cold fill disk then warm re-score (fit≠eval)",
            "mechanism": "PackScoreCache RAM+disk; TCACHE elig-only code on warm hit",
            "parent": "PFB2 K=2 banks (formal genes; decode once)",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
