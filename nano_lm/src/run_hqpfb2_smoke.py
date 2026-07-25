"""Smoke H-ABS-QPFB2: PFB K=2 on QT-int8; wall↓ vs QPFB k=4."""

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
from pfb_ops import K_BEAMS, PFB_TEMP
from pfb_score import (
    arm_means,
    attach_code_teacher,
    collect_beam_banks,
    collect_pfb_banks,
    commit_pfb_rows,
)
from prog_packs import PROG_PROMPTS, build_prog_pack
from qpfb2_ops import decide_hqpfb2
from qt_ops import QT_BITS
from qt_quant import quantize_student_int8, weight_nbytes
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10005
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
        print("ERROR: H-ABS-QPFB2 requires CUDA", file=sys.stderr)
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
    banks4: list[dict[str, Any]] = []
    banks2: list[dict[str, Any]] = []
    nbytes = 0
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "decode_qt", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        qt = quantize_student_int8(student)  # type: ignore[arg-type]
        qt.to(device)
        nbytes = weight_nbytes(qt)
        gene = _early_gene(out, seed)
        claim = seed + _CLAIM
        p_part, b4 = collect_pfb_banks(
            story_teacher=story,
            student=qt,
            prompts=texts,
            gene=gene,
            max_new=_MAX_NEW,
            seed=claim,
            k=K_BEAMS,
            temperature=PFB_TEMP,
            parent_family="H-QT-int8",
            weight_bytes=nbytes,
        )
        b2 = collect_beam_banks(
            story_teacher=story,
            student=qt,
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
        _free_cuda(story, student, qt)
    print(json.dumps({"phase": "code_commit", "teacher": meta["hf_id"]}), flush=True)
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    parent_rows = attach_code_teacher(code, parent_rows)
    parent_code = {
        (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
        for r in parent_rows
    }
    qpfb4_rows = commit_pfb_rows(
        code,
        banks4,
        parent_code_by_key=parent_code,
        family="H-ABS-QPFB",
        weight_bytes=nbytes,
    )
    qpfb2_rows = commit_pfb_rows(
        code,
        banks2,
        parent_code_by_key=parent_code,
        family="H-ABS-QPFB2",
        weight_bytes=nbytes,
    )
    _free_cuda(code)
    parent_m, qpfb4_m, qpfb2_m = (
        arm_means(parent_rows),
        arm_means(qpfb4_rows),
        arm_means(qpfb2_rows),
    )
    decision = decide_hqpfb2(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        qpfb2_story=float(qpfb2_m["mean_story_lp"]),
        qpfb2_code=float(qpfb2_m["mean_code_lp"]),
        mean_unique=float(qpfb2_m["mean_unique"]),
        mean_elig=float(qpfb2_m["mean_elig"]),
        mean_switch=float(qpfb2_m["mean_switch"]),
        qpfb2_wall=float(qpfb2_m["mean_wall_ms"]),
        qpfb4_wall=float(qpfb4_m["mean_wall_ms"]),
        identical=_identical(parent_rows, qpfb2_rows),
    )
    payload = {
        "rows_parent": parent_rows,
        "rows_qpfb4": qpfb4_rows,
        "rows_qpfb2": qpfb2_rows,
        "parent_means": parent_m,
        "qpfb4_means": qpfb4_m,
        "qpfb2_means": qpfb2_m,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "pack": {k: pack[k] for k in ("name","n_prompts","target_tokens","source")},
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "k2": K2_BEAMS,
        "k4": K_BEAMS,
        "pfb_temp": PFB_TEMP,
        "bits": QT_BITS,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "QPFB2: QT-int8 + PFB K=2 vs QT; wall↓ vs QPFB k=4",
        "mechanism": "quantize_student_int8 then PFB K=2; wall gate vs QPFB k=4",
        "parent": "H-QT int8 EARLY n=1 on B2",
    }
    write_json(out / "hqpfb2_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "hqpfb2_smoke.json")}))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
