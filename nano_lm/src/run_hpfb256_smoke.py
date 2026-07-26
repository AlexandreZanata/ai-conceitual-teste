"""Smoke H-PFB256: PFB2 on prog@256 vs EARLY@256; wall vs @128."""

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
from pfb256_ops import PFB256_TARGET, REF128_TARGET, decide_hpfb256
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
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10041
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


def _stubs_for_prompts(
    template: list[dict[str, Any]], texts: list[str]
) -> list[dict[str, Any]]:
    """Parent-shaped rows with replaced prompts (beam-only decode)."""
    out: list[dict[str, Any]] = []
    for i, text in enumerate(texts):
        base = template[i % len(template)]
        out.append({**base, "prompt": text})
    return out


def main() -> int:
    for key in _PROXY:
        os.environ.pop(key, None)
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-PFB256 requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    assert_disjoint(load_prompt_ids(c["prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(OOD_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    assert_disjoint(load_prompt_ids(DOM_PROMPTS), load_prompt_ids(PROG_PROMPTS))
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack256 = build_prog_pack(tok, target_tokens=PFB256_TARGET)
    pack128 = build_prog_pack(tok, target_tokens=REF128_TARGET)
    meta = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks256: list[dict[str, Any]] = []
    walls_128: list[float] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "decode_256", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(out, seed)
        claim = seed + _CLAIM
        p_part, _ = collect_pfb_banks(
            story_teacher=story,
            student=student,
            prompts=pack256["texts"],
            gene=gene,
            max_new=_MAX_NEW,
            seed=claim,
            k=1,
            temperature=PFB_TEMP,
            parent_family="H-EARLY@256",
        )
        b256 = collect_beam_banks(
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
        print(json.dumps({"phase": "decode_128_wall", "seed": seed}), flush=True)
        stubs = _stubs_for_prompts(p_part, pack128["texts"])
        b128 = collect_beam_banks(
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
        banks256.extend(b256)
        walls_128.extend(float(b["wall_ms"]) for b in b128)
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
    pfb_rows = commit_pfb_rows(
        code,
        banks256,
        parent_code_by_key=parent_code,
        family="H-PFB256",
    )
    _free_cuda(code)
    parent_m, pfb_m = arm_means(parent_rows), arm_means(pfb_rows)
    wall_256 = float(pfb_m["mean_wall_ms"])
    wall_128 = sum(walls_128) / max(len(walls_128), 1)
    decision = decide_hpfb256(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        pfb256_story=float(pfb_m["mean_story_lp"]),
        pfb256_code=float(pfb_m["mean_code_lp"]),
        mean_unique=float(pfb_m["mean_unique"]),
        mean_elig=float(pfb_m["mean_elig"]),
        mean_switch=float(pfb_m["mean_switch"]),
        wall_256=wall_256,
        wall_128=wall_128,
        identical=_identical(parent_rows, pfb_rows),
    )
    payload = {
        "rows_parent": parent_rows,
        "rows_pfb256": pfb_rows,
        "parent_means": parent_m,
        "pfb256_means": pfb_m,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "wall_256_ms": wall_256,
        "wall_128_ms": wall_128,
        "pack256": {
            k: pack256[k] for k in ("name", "n_prompts", "target_tokens", "source")
        },
        "pack128": {
            k: pack128[k] for k in ("name", "n_prompts", "target_tokens", "source")
        },
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "k": K2_BEAMS,
        "pfb_temp": PFB_TEMP,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "PFB256: PFB2 on prog@256 vs EARLY@256; wall vs @128",
        "mechanism": "elongate like DOM to L=256; BEAMKV shared KV; not CTX chunk",
        "parent": "H-EARLY n=1 @256 on B2",
    }
    write_json(out / "hpfb256_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "hpfb256_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
