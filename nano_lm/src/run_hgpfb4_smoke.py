"""Smoke H-ABS-GPFB4: PFB K=4 under frozen GENC genome (GPFB lesson)."""

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
from genc_ops import clamp_genc_gene
from genc_prompt import load_prog_chunks
from gpfb4_ops import K_BEAMS, PFB_TEMP, decide_hgpfb4
from gpfb4_score import collect_gpfb4_banks
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, ROOT, matrix_cfg, write_json
from pfb_score import arm_means, attach_code_teacher, commit_pfb_rows
from prog_packs import PROG_PROMPTS, build_prog_pack
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10017
_MAX_NEW = 32
_PROXY = (
    "http_proxy",
    "https_proxy",
    "HTTP_PROXY",
    "HTTPS_PROXY",
    "ALL_PROXY",
    "all_proxy",
)
_SMOKE = REPO / "results/nano-lm/student-matrix/hgenc_smoke.json"


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return {**gene, "n": 1, "temperature": 1e-6}


def _load_smoke_genes() -> list[dict[str, Any]]:
    data = json.loads(_SMOKE.read_text(encoding="utf-8"))
    genes = data.get("best_genes")
    if not isinstance(genes, list) or not genes:
        raise ValueError(f"missing best_genes in {_SMOKE}")
    return [clamp_genc_gene(g) for g in genes]


def _free_cuda(*objs: object) -> None:
    for obj in objs:
        del obj
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def _identical(a: list[dict[str, Any]], b: list[dict[str, Any]]) -> bool:
    return len(a) == len(b) and all(
        str(x["continuation"]) == str(y["continuation"])
        for x, y in zip(a, b)
    )


def main() -> int:
    for key in _PROXY:
        os.environ.pop(key, None)
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-ABS-GPFB4 requires CUDA", file=sys.stderr)
        return 2
    assert_disjoint(
        load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"])
    )
    assert_disjoint(
        load_prompt_ids(c["prompts"]), load_prompt_ids(PROG_PROMPTS)
    )
    assert_disjoint(
        load_prompt_ids(c["fit_prompts"]), load_prompt_ids(PROG_PROMPTS)
    )
    assert_disjoint(
        load_prompt_ids(OOD_PROMPTS), load_prompt_ids(PROG_PROMPTS)
    )
    assert_disjoint(
        load_prompt_ids(DOM_PROMPTS), load_prompt_ids(PROG_PROMPTS)
    )
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    tok = load_tokenizer(c["tokenizer_id"], c["cache"])
    pack = build_prog_pack(tok)
    texts = list(pack["texts"])
    chunks = load_prog_chunks(ROOT / "data" / "curated")
    genes = _load_smoke_genes()
    meta = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks: list[dict[str, Any]] = []
    nbytes = 0
    t0 = time.perf_counter()
    for i, seed in enumerate(c["seeds"]):
        print(json.dumps({"phase": "decode_genc", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        early = _early_gene(out, seed)
        gene = genes[i % len(genes)]
        claim = seed + _CLAIM
        p_part, b_part, nbytes = collect_gpfb4_banks(
            story_teacher=story,
            student=student,
            prompts=texts,
            genc_gene=gene,
            early=early,
            chunks=chunks,
            max_new=_MAX_NEW,
            seed=claim,
            k=K_BEAMS,
            temperature=PFB_TEMP,
        )
        parent_rows.extend(p_part)
        banks.extend(b_part)
        _free_cuda(story, student)
    print(
        json.dumps({"phase": "code_commit", "teacher": meta["hf_id"]}),
        flush=True,
    )
    code = load_causal_lm(
        meta["hf_id"], meta["tokenizer_id"], cache_dir=c["cache"], use_fp16=True
    )
    parent_rows = attach_code_teacher(code, parent_rows)
    parent_code = {
        (str(r["prompt"]), int(r["seed"])): float(r["code_teacher_lp"])
        for r in parent_rows
    }
    gpfb4 = commit_pfb_rows(
        code,
        banks,
        parent_code_by_key=parent_code,
        family="H-ABS-GPFB4",
        weight_bytes=nbytes,
    )
    _free_cuda(code)
    parent_m, m4 = arm_means(parent_rows), arm_means(gpfb4)
    decision = decide_hgpfb4(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        gpfb4_story=float(m4["mean_story_lp"]),
        gpfb4_code=float(m4["mean_code_lp"]),
        mean_unique=float(m4["mean_unique"]),
        mean_elig=float(m4["mean_elig"]),
        mean_switch=float(m4["mean_switch"]),
        k=K_BEAMS,
        identical=_identical(parent_rows, gpfb4),
    )
    payload = {
        "rows_parent": parent_rows,
        "rows_gpfb4": gpfb4,
        "parent_means": parent_m,
        "gpfb4_means": m4,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "pack": {
            k: pack[k] for k in ("name", "n_prompts", "target_tokens", "source")
        },
        "best_genes": genes,
        "n_chunks": len(chunks),
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "k": K_BEAMS,
        "pfb_temp": PFB_TEMP,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "GPFB4: GENC genome + PFB K=4 vs GENC-serial",
        "mechanism": (
            "frozen GENC gene; serial decode on GENC ctx; PFB K=4 "
            "(GPFB K=2 KILL lesson)"
        ),
        "parent": "H-GENC-serial n=1 (same genome, no beam)",
        "smoke_source": str(_SMOKE),
    }
    write_json(out / "hgpfb4_smoke.json", payload)
    print(
        json.dumps(
            {"decision": decision, "out": str(out / "hgpfb4_smoke.json")}
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
