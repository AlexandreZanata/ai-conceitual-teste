"""Smoke H-GENC: evolve context/serve genome under BUD vs PACK/EARLY parent."""

from __future__ import annotations

import json
import os
import random
import sys
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from dom_packs import DOM_PROMPTS
from eval_decode import load_pair
from genc_ops import (
    POP_MAX,
    clamp_genc_gene,
    decide_hgenc,
    mutate_genc_gene,
    parent_genc_gene,
    pareto_front_indices,
    random_genc_gene,
)
from genc_prompt import load_prog_chunks
from genc_score import arm_means, attach_code_teacher, fit_score, score_gene_rows
from hold_ops import assert_disjoint, load_prompt_ids
from load_model import load_causal_lm, resolve_device
from matrix_common import ROOT, matrix_cfg, write_json
from prog_packs import PROG_PROMPTS, build_prog_pack
from tchr_ops import STORY_TEACHER_ID, code_teacher_meta
from tipd_pair import tune_cpu_threads
from xfer_packs import OOD_PROMPTS

_CLAIM = 9981
_MAX_NEW = 32
_POP = 6
_GENS = 2
_FIT_N = 2


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


def _evolve(
    *,
    story: Any,
    student: Any,
    early: dict[str, Any],
    fit_prompts: list[str],
    chunks: list[str],
    seed: int,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    rng = random.Random(seed + 4242)
    pop = [random_genc_gene(rng) for _ in range(_POP)]
    pop[0] = parent_genc_gene()
    history: list[dict[str, Any]] = []
    best = pop[0]
    best_s = float("-inf")
    for gen in range(_GENS):
        scored: list[tuple[float, dict[str, Any]]] = []
        for i, gene in enumerate(pop):
            rows = score_gene_rows(
                story_teacher=story,
                student=student,
                prompts=fit_prompts,
                gene=gene,
                early=early,
                chunks=chunks,
                max_new=_MAX_NEW,
                seed=seed + 100 * gen + i,
                family="H-GENC-fit",
            )
            s = fit_score(rows)
            scored.append((s, clamp_genc_gene(gene)))
            if s > best_s:
                best_s = s
                best = scored[-1][1]
        scored.sort(key=lambda t: t[0], reverse=True)
        history.append(
            {
                "gen": gen,
                "best_fit": scored[0][0],
                "best_gene": scored[0][1],
            }
        )
        elites = [g for _, g in scored[: max(1, _POP // 2)]]
        pop = [
            mutate_genc_gene(elites[i % len(elites)], rng) for i in range(_POP)
        ]
    return best, history


def main() -> int:
    _clear_broken_proxy()
    assert _POP <= POP_MAX
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("ERROR: H-GENC requires CUDA", file=sys.stderr)
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
    texts = list(pack["texts"])
    fit_prompts = texts[:_FIT_N]
    claim_prompts = texts[_FIT_N:]
    if len(claim_prompts) < 1:
        print("ERROR: need ≥1 claim prog prompt after fit split", file=sys.stderr)
        return 2
    assert_disjoint(
        [f"fit{i}" for i in range(len(fit_prompts))],
        [f"claim{i}" for i in range(len(claim_prompts))],
    )
    chunks = load_prog_chunks(ROOT / "data" / "curated")
    meta = code_teacher_meta()
    parent_rows: list[dict[str, Any]] = []
    best_rows: list[dict[str, Any]] = []
    histories: list[Any] = []
    best_genes: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    parent_gene = parent_genc_gene()
    for seed in c["seeds"]:
        print(json.dumps({"phase": "evolve", "seed": seed}), flush=True)
        ckpt = out / f"B2_seed{seed}.pt"
        story, student = load_pair(
            ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
        )
        early = _early_gene(out, seed)
        claim = seed + _CLAIM
        best, hist = _evolve(
            story=story,
            student=student,
            early=early,
            fit_prompts=fit_prompts,
            chunks=chunks,
            seed=seed,
        )
        histories.append(hist)
        best_genes.append(best)
        parent_rows.extend(
            score_gene_rows(
                story_teacher=story,
                student=student,
                prompts=claim_prompts,
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
                prompts=claim_prompts,
                gene=best,
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
    front = pareto_front_indices([parent_m, best_m])
    decision = decide_hgenc(
        parent=parent_m, best=best_m, n_rows=int(best_m.get("n", 0))
    )
    payload = {
        "parent_rows": parent_rows,
        "best_rows": best_rows,
        "parent_means": parent_m,
        "best_means": best_m,
        "best_genes": best_genes,
        "parent_gene": parent_gene,
        "history": histories,
        "pareto_front_indices": front,
        "decision": decision,
        "wall_s": time.perf_counter() - t0,
        "pack": {
            "name": pack["name"],
            "n_prompts": pack["n_prompts"],
            "target_tokens": pack["target_tokens"],
            "source": pack["source"],
        },
        "pop": _POP,
        "gens": _GENS,
        "n_chunks": len(chunks),
        "mechanism": (
            "genetic serve genome {k_retrieve,chunk_len,stride,quant_bits,"
            "exit_depth} under BUD; fit≠eval; Pareto vs PACK/EARLY"
        ),
        "story_teacher": {"hf_id": STORY_TEACHER_ID, "role": "story_teacher"},
        "code_teacher": meta,
        "max_new": _MAX_NEW,
        "cpu_threads": threads,
        "mode": "GENC: evolve context/serve knobs vs PACK/EARLY parent on prog@128",
    }
    write_json(out / "hgenc_smoke.json", payload)
    print(json.dumps({"decision": decision, "out": str(out / "hgenc_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
