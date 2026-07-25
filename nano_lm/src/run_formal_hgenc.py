"""Formal H-GENC: freeze smoke best genes; eval vs parent on full prog pack."""

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
from genc_ops import clamp_genc_gene, decide_hgenc, parent_genc_gene
from genc_prompt import load_prog_chunks
from genc_score import arm_means, attach_code_teacher, score_gene_rows
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, ROOT, write_json
from prog_packs import PROG_PROMPTS, build_prog_pack
from run_formal_hprog import formal_cfg as hprog_formal_cfg
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 9982
_MAX_NEW = 32
_SMOKE = REPO / "results/nano-lm/student-matrix/hgenc_smoke.json"


def formal_cfg() -> dict[str, Any]:
    base = hprog_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hgenc"
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


def _load_smoke_genes() -> list[dict[str, Any]]:
    data = json.loads(_SMOKE.read_text(encoding="utf-8"))
    genes = data.get("best_genes")
    if not isinstance(genes, list) or not genes:
        raise ValueError(f"missing best_genes in {_SMOKE}")
    return [clamp_genc_gene(g) for g in genes]


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
        print("ERROR: H-GENC formal requires CUDA", file=sys.stderr)
        return 2
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    early_dir = Path(c["early_dir"])
    ckpt_dir = Path(c["ckpt_dir"])
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok)
    texts = list(pack["texts"])
    chunks = load_prog_chunks(ROOT / "data" / "curated")
    meta = code_teacher_meta()
    smoke_genes = _load_smoke_genes()
    parent_gene = parent_genc_gene()
    parent_rows: list[dict[str, Any]] = []
    best_rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for i, seed in enumerate(c["seeds"]):
        print(json.dumps({"phase": "story_decode", "seed": seed}), flush=True)
        ckpt = ckpt_dir / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        early = _early_gene(early_dir, seed)
        claim = seed + _CLAIM
        gene = smoke_genes[i % len(smoke_genes)]
        parent_rows.extend(
            score_gene_rows(
                story_teacher=story,
                student=student,
                prompts=texts,
                gene=parent_gene,
                early=early,
                chunks=chunks,
                max_new=_MAX_NEW,
                seed=claim,
                family="H-EARLY-parent",
            )
        )
        best_rows.extend(
            score_gene_rows(
                story_teacher=story,
                student=student,
                prompts=texts,
                gene=gene,
                early=early,
                chunks=chunks,
                max_new=_MAX_NEW,
                seed=claim + 50,
                family="H-GENC-best",
            )
        )
        _free_cuda(story, student)
    print(json.dumps({"phase": "code_score", "teacher": meta["hf_id"]}), flush=True)
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    parent_rows = attach_code_teacher(code, parent_rows)
    best_rows = attach_code_teacher(code, best_rows)
    _free_cuda(code)
    parent_m = arm_means(parent_rows)
    best_m = arm_means(best_rows)
    decision = decide_hgenc(
        parent=parent_m, best=best_m, n_rows=int(best_m.get("n", 0))
    )
    payload = {
        "parent_rows": parent_rows,
        "best_rows": best_rows,
        "parent_means": parent_m,
        "best_means": best_m,
        "best_genes": smoke_genes,
        "parent_gene": parent_gene,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "pack": {
            "name": pack["name"],
            "n_prompts": pack["n_prompts"],
            "target_tokens": pack["target_tokens"],
            "source": pack["source"],
        },
        "n_chunks": len(chunks),
        "mechanism": (
            "formal: freeze smoke best genomes; full prog@128 eval under BUD"
        ),
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "formal GENC vs PACK/EARLY parent (genes frozen from smoke)",
        "smoke_source": str(_SMOKE),
    }
    write_json(out / "formal.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
