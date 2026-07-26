"""Smoke H-GPFB4-LONG: GPFB4 K=4 on ROLL vs GENC-serial; wall vs full."""

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
from gpfb4_score import collect_gpfb4_banks
from gpfb4long_ops import (
    K_BEAMS,
    PFB_TEMP,
    ROLL_S,
    ROLL_TARGET,
    ROLL_W,
    decide_hgpfb4long,
)
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import REPO, ROOT, matrix_cfg, write_json
from pfb_score import arm_means, attach_code_teacher, commit_pfb_rows
from prog_packs import PROG_PROMPTS, build_prog_pack
from roll_ctx import expand_roll_prompts
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 10081
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
        print("ERROR: H-GPFB4-LONG requires CUDA", file=sys.stderr)
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
    texts = list(pack["texts"])
    rolled, meta = expand_roll_prompts(tok, texts, w=ROLL_W, s=ROLL_S)
    l_eff = float(sum(m["l_eff"] for m in meta) / max(len(meta), 1))
    mean_active = float(
        sum(m["active_len"] for m in meta) / max(len(meta), 1)
    )
    chunks = load_prog_chunks(ROOT / "data" / "curated")
    genes = _load_smoke_genes()
    meta_t = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    banks_roll: list[dict[str, Any]] = []
    banks_full: list[dict[str, Any]] = []
    nbytes = 0
    t0 = time.perf_counter()
    for i, seed in enumerate(c["seeds"]):
        print(json.dumps({"phase": "decode_roll", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        early = _early_gene(out, seed)
        gene = genes[i % len(genes)]
        claim = seed + _CLAIM
        p_part, b_roll, nbytes = collect_gpfb4_banks(
            story_teacher=story,
            student=student,
            prompts=rolled,
            genc_gene=gene,
            early=early,
            chunks=chunks,
            max_new=_MAX_NEW,
            seed=claim,
            k=K_BEAMS,
            temperature=PFB_TEMP,
        )
        parent_rows.extend(p_part)
        banks_roll.extend(b_roll)
        print(json.dumps({"phase": "decode_full", "seed": seed}), flush=True)
        _, b_full, _ = collect_gpfb4_banks(
            story_teacher=story,
            student=student,
            prompts=texts,
            genc_gene=gene,
            early=early,
            chunks=chunks,
            max_new=_MAX_NEW,
            seed=claim + 100,
            k=K_BEAMS,
            temperature=PFB_TEMP,
        )
        banks_full.extend(b_full)
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
    long_rows = commit_pfb_rows(
        code,
        banks_roll,
        parent_code_by_key=parent_code,
        family="H-GPFB4-LONG",
        weight_bytes=nbytes,
    )
    full_rows = commit_pfb_rows(
        code,
        banks_full,
        parent_code_by_key={},
        family="H-GPFB4-FULL",
        weight_bytes=nbytes,
    )
    _free_cuda(code)
    parent_m = arm_means(parent_rows)
    long_m = arm_means(long_rows)
    full_m = arm_means(full_rows)
    decision = decide_hgpfb4long(
        parent_story=float(parent_m["mean_story_lp"]),
        parent_code=float(parent_m["mean_code_lp"]),
        long_story=float(long_m["mean_story_lp"]),
        long_code=float(long_m["mean_code_lp"]),
        mean_unique=float(long_m["mean_unique"]),
        mean_elig=float(long_m["mean_elig"]),
        mean_switch=float(long_m["mean_switch"]),
        k=K_BEAMS,
        identical=_identical(parent_rows, long_rows),
        l_eff=l_eff,
        mean_active=mean_active,
        wall_roll=float(long_m["mean_wall_ms"]),
        wall_full=float(full_m["mean_wall_ms"]),
    )
    write_json(
        out / "hgpfb4long_smoke.json",
        {
            "rows_parent": parent_rows,
            "rows_long": long_rows,
            "rows_full": full_rows,
            "parent_means": parent_m,
            "long_means": long_m,
            "full_means": full_m,
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
            "best_genes": genes,
            "n_chunks": len(chunks),
            "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
            "code_teacher": meta_t,
            "k": K_BEAMS,
            "pfb_temp": PFB_TEMP,
            "max_new": _MAX_NEW,
            "cpu_threads": threads,
            "mode": (
                "GPFB4-LONG: GENC∘PFB K=4 on ROLL vs GENC-serial; "
                "wall vs full-prefill GPFB4"
            ),
            "mechanism": (
                "compose GPFB4+ROLL (Y4/Y5); never K=2; not GENCACHE/STREAM"
            ),
            "parent": "H-GENC-serial n=1 on rolled ctx",
            "smoke_source": str(_SMOKE),
        },
    )
    print(
        json.dumps(
            {
                "decision": decision,
                "out": str(out / "hgpfb4long_smoke.json"),
            }
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
