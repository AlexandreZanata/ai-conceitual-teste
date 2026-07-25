"""Smoke H-QT: int8 weight-only EARLY serve vs fp parent on prog@128."""

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
from prog_packs import PROG_PROMPTS, build_prog_pack
from qt_ops import QT_BITS, decide_hqt
from qt_quant import quantize_student_int8, weight_nbytes
from qt_score import arm_means, attach_code_teacher, collect_early_rows
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 9970
_MAX_NEW = 32


def _clear_broken_proxy() -> None:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)


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


def main() -> int:
    _clear_broken_proxy()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-QT requires CUDA", file=sys.stderr)
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
    fp_rows: list[dict[str, Any]] = []
    qt_rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "story_decode", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(out, seed)
        claim = seed + _CLAIM
        fp_bytes = weight_nbytes(student)  # type: ignore[arg-type]
        fp_rows.extend(
            collect_early_rows(
                story_teacher=story,
                student=student,
                prompts=texts,
                gene=gene,
                max_new=_MAX_NEW,
                seed=claim,
                family="H-EARLY-fp",
                weight_bytes=fp_bytes,
            )
        )
        qt_student = quantize_student_int8(student)  # type: ignore[arg-type]
        qt_student.to(device)
        qt_bytes = weight_nbytes(qt_student)
        qt_rows.extend(
            collect_early_rows(
                story_teacher=story,
                student=qt_student,
                prompts=texts,
                gene=gene,
                max_new=_MAX_NEW,
                seed=claim + 50,
                family="H-QT-int8",
                weight_bytes=qt_bytes,
            )
        )
        _free_cuda(story, student, qt_student)
    print(json.dumps({"phase": "code_score", "teacher": meta["hf_id"]}), flush=True)
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    fp_rows = attach_code_teacher(code, fp_rows)
    qt_rows = attach_code_teacher(code, qt_rows)
    _free_cuda(code)
    fp_m = arm_means(fp_rows)
    qt_m = arm_means(qt_rows)
    decision = decide_hqt(parent=fp_m, qt=qt_m, n_rows=int(qt_m.get("n", 0)))
    payload = {
        "fp_rows": fp_rows,
        "qt_rows": qt_rows,
        "fp_means": fp_m,
        "qt_means": qt_m,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "pack": {
            "name": pack["name"],
            "n_prompts": pack["n_prompts"],
            "target_tokens": pack["target_tokens"],
            "source": pack["source"],
        },
        "bits": QT_BITS,
        "mechanism": "int8 weight-only Linear (skip lm_head; dequant to act dtype)",
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "QT: int8 weight-only EARLY serve vs fp on prog@128 (PACK tip)",
    }
    write_json(out / "hqt_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "hqt_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
