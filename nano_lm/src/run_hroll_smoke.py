"""Smoke H-ROLL: PFB2 on rolled summary‖W vs EARLY; L_eff≫W; mem≈O(W)."""

from __future__ import annotations

import json
import os
import sys
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
from matrix_common import matrix_cfg, write_json
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
from roll_ctx import expand_roll_prompts
from roll_ops import ROLL_S, ROLL_TARGET, ROLL_W, decide_hroll
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10051
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
        print("ERROR: H-ROLL requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(DOM_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok, target_tokens=ROLL_TARGET)
    rolled, meta = expand_roll_prompts(
        tok, pack["texts"], w=ROLL_W, s=ROLL_S
    )
    l_eff = float(sum(m["l_eff"] for m in meta) / max(len(meta), 1))
    mean_active = float(
        sum(m["active_len"] for m in meta) / max(len(meta), 1)
    )
    meta_t = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "decode_roll", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(out, seed)
        claim = seed + _CLAIM
        p_part, _ = collect_pfb_banks(
            story_teacher=story,
            student=student,
            prompts=rolled,
            gene=gene,
            max_new=_MAX_NEW,
            seed=claim,
            k=1,
            temperature=PFB_TEMP,
            parent_family="H-EARLY@ROLL",
        )
        b_part = collect_beam_banks(
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
        parent_rows.extend(p_part)
        banks.extend(b_part)
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
    roll_rows = commit_pfb_rows(
        code, banks, parent_code_by_key=parent_code, family="H-ROLL"
    )
    _free_cuda(code)
    parent_m, roll_m = arm_means(parent_rows), arm_means(roll_rows)
    decision = decide_hroll(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        roll_story=float(roll_m["mean_story_lp"]),
        roll_code=float(roll_m["mean_code_lp"]),
        mean_unique=float(roll_m["mean_unique"]),
        mean_elig=float(roll_m["mean_elig"]),
        mean_switch=float(roll_m["mean_switch"]),
        l_eff=l_eff,
        mean_active=mean_active,
        identical=_identical(parent_rows, roll_rows),
    )
    write_json(
        out / "hroll_smoke.json",
        {
            "rows_parent": parent_rows,
            "rows_roll": roll_rows,
            "parent_means": parent_m,
            "roll_means": roll_m,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "l_eff": l_eff,
            "mean_active": mean_active,
            "w": ROLL_W,
            "s": ROLL_S,
            "n_segments": len(meta),
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
            "mode": "ROLL: PFB2 on summary‖W segments vs EARLY",
            "mechanism": "stride-summary cache + window W; BEAMKV; not CTX",
            "parent": "H-EARLY n=1 on rolled ctx",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "hroll_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
