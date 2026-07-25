"""Formal H-TCHR: code teacher wire on prog@128 (fit≠eval genes)."""

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
from prog_packs import PROG_PROMPTS, build_prog_pack
from run_formal_hprog import formal_cfg as hprog_formal_cfg
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta, decide_htchr
from tchr_score import (
    collect_early_story_rows,
    dual_means,
    score_rows_code_teacher,
)
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 9920
_MAX_NEW = 32


def formal_cfg() -> dict[str, Any]:
    base = hprog_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-htchr"
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
        raise RuntimeError("H-TCHR formal requires CUDA")
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    early_dir = Path(c["early_dir"])
    ckpt_dir = Path(c["ckpt_dir"])
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok)
    texts = pack["texts"]
    meta = code_teacher_meta()
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        print(
            json.dumps(
                {
                    "phase": "story_decode",
                    "seed": seed,
                    "teacher": STORY_TEACHER_ID,
                }
            ),
            flush=True,
        )
        ckpt = ckpt_dir / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        gene = _early_gene(early_dir, seed)
        rows.extend(
            collect_early_story_rows(
                teacher=story,
                student=student,
                prompts=texts,
                gene=gene,
                max_new=_MAX_NEW,
                seed=seed + _CLAIM,
            )
        )
        _free_cuda(story, student)
    print(
        json.dumps({"phase": "code_score", "teacher": meta["hf_id"]}),
        flush=True,
    )
    code = load_causal_lm(
        meta["hf_id"],
        meta["tokenizer_id"],
        cache_dir=c["cache"],
        use_fp16=True,
    )
    rows = score_rows_code_teacher(code, rows)
    _free_cuda(code)
    means = dual_means(rows)
    decision = decide_htchr(
        code_teacher=meta,
        mean_story_lp=float(means["mean_story_lp"]),
        mean_code_lp=float(means["mean_code_lp"]),
        n_rows=int(means["n"]),
    )
    write_json(
        out / "formal.json",
        {
            "rows": rows,
            "means": means,
            "decision": decision,
            "wall_s": time.perf_counter() - t0,
            "pack": {
                "name": pack["name"],
                "n_prompts": pack["n_prompts"],
                "target_tokens": pack["target_tokens"],
                "source": pack["source"],
            },
            "story_teacher": {
                "hf_id": STORY_TEACHER_ID,
                "role": "story_teacher",
            },
            "code_teacher": meta,
            "max_new": _MAX_NEW,
            "cpu_threads": threads,
            "mode": "TCHR: code_teacher_lp on EARLY prog@128 (dual vs story)",
        },
    )
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
