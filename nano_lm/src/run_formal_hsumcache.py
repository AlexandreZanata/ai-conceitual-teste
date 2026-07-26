"""Formal H-SUMCACHE: summary+tail PFB2 vs EARLY; wall < full (fit≠eval)."""

from __future__ import annotations

import json
import os
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from decode_beamkv import decode_beams_shared_kv
from dom_packs import DOM_PROMPTS
from eval_decode import load_pair
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, write_json
from pfb2_ops import K2_BEAMS
from pfb_ops import PFB_TEMP
from pfb_score import (
    arm_means,
    attach_code_teacher,
    collect_beam_banks,
    collect_pfb_banks,
    commit_pfb_rows,
)
from prog_packs import PROG_PROMPTS, build_prog_pack
from run_formal_hprog import formal_cfg as hprog_formal_cfg
from sumcache_ctx import expand_sumcache_prompts
from sumcache_ops import (
    SUMCACHE_S_COARSE,
    SUMCACHE_S_FINE,
    SUMCACHE_TARGET,
    SUMCACHE_W,
    decide_hsumcache,
)
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10073
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
    base["out"] = REPO / "results/nano-lm/formal-hsumcache"
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
    return len(a) == len(b) and all(
        str(x["continuation"]) == str(y["continuation"]) for x, y in zip(a, b)
    )


def _stubs(template: list[dict[str, Any]], texts: list[str]) -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for i, text in enumerate(texts):
        base = template[i % len(template)]
        out.append({**base, "prompt": text})
    return out


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
        raise RuntimeError("H-SUMCACHE formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    early_dir = Path(c["early_dir"])
    ckpt_dir = Path(c["ckpt_dir"])
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok, target_tokens=SUMCACHE_TARGET)
    sum_prompts, full_prompts, meta = expand_sumcache_prompts(tok, pack["texts"])
    l_eff = float(sum(m["l_eff"] for m in meta) / max(len(meta), 1))
    mean_active = float(
        sum(m["active_len"] for m in meta) / max(len(meta), 1)
    )
    meta_t = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks_sum: list[dict[str, Any]] = []
    walls_full: list[float] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "sumcache", "seed": seed}), flush=True)
        ckpt = ckpt_dir / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(early_dir, seed)
        claim = seed + _CLAIM
        p_part, _ = collect_pfb_banks(
            story_teacher=story,
            student=student,
            prompts=sum_prompts,
            gene=gene,
            max_new=_MAX_NEW,
            seed=claim,
            k=1,
            temperature=PFB_TEMP,
            parent_family="H-EARLY@SUM",
        )
        b_sum = collect_beam_banks(
            story_teacher=story,
            student=student,
            parent_rows=p_part,
            gene=gene,
            max_new=_MAX_NEW,
            beam_seed=claim + 2000,
            k=K2_BEAMS,
            temperature=PFB_TEMP,
            decode_beams_fn=decode_beams_shared_kv,
        )
        print(json.dumps({"phase": "full_wall", "seed": seed}), flush=True)
        stubs = _stubs(p_part, full_prompts)
        b_full = collect_beam_banks(
            story_teacher=story,
            student=student,
            parent_rows=stubs,
            gene=gene,
            max_new=_MAX_NEW,
            beam_seed=claim + 6000,
            k=K2_BEAMS,
            temperature=PFB_TEMP,
            decode_beams_fn=decode_beams_shared_kv,
        )
        parent_rows.extend(p_part)
        banks_sum.extend(b_sum)
        walls_full.extend(float(b["wall_ms"]) for b in b_full)
        _free_cuda(story, student)
    print(json.dumps({"phase": "code_commit", "teacher": meta_t["hf_id"]}), flush=True)
    code = load_causal_lm(
        meta_t["hf_id"], meta_t["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    parent_rows = attach_code_teacher(code, parent_rows)
    parent_code = {
        (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
        for r in parent_rows
    }
    sum_rows = commit_pfb_rows(
        code, banks_sum, parent_code_by_key=parent_code, family="H-SUMCACHE"
    )
    _free_cuda(code)
    parent_m, sum_m = arm_means(parent_rows), arm_means(sum_rows)
    wall_sum = float(sum_m["mean_wall_ms"])
    wall_full = sum(walls_full) / max(len(walls_full), 1)
    decision = decide_hsumcache(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        sum_story=float(sum_m["mean_story_lp"]),
        sum_code=float(sum_m["mean_code_lp"]),
        mean_unique=float(sum_m["mean_unique"]),
        mean_elig=float(sum_m["mean_elig"]),
        mean_switch=float(sum_m["mean_switch"]),
        l_eff=l_eff,
        mean_active=mean_active,
        wall_sum=wall_sum,
        wall_full=wall_full,
        identical=_identical(parent_rows, sum_rows),
    )
    write_json(
        out / "formal.json",
        {
            "rows_parent": parent_rows,
            "rows_sumcache": sum_rows,
            "parent_means": parent_m,
            "sumcache_means": sum_m,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "l_eff": l_eff,
            "mean_active": mean_active,
            "wall_sum_ms": wall_sum,
            "wall_full_ms": wall_full,
            "w": SUMCACHE_W,
            "s_coarse": SUMCACHE_S_COARSE,
            "s_fine": SUMCACHE_S_FINE,
            "pack": {
                k: pack[k]
                for k in ("name", "n_prompts", "target_tokens", "source")
            },
            "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
            "code_teacher": meta_t,
            "k": K2_BEAMS,
            "pfb_temp": PFB_TEMP,
            "max_new": _MAX_NEW,
            "cpu_threads": threads,
            "mode": "SUMCACHE formal: summary+tail vs EARLY; wall vs full (fit≠eval)",
            "mechanism": "GENC-scale hierarchical compress; BEAMKV; not CTX",
            "parent": "H-EARLY n=1 on summary+tail (formal genes)",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
