"""Formal H-LAY: layer early-exit search vs frozen formal H-EARLY tip."""

from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any

import torch
import yaml

from decode_early import decode_early
from eval_decode import load_pair
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from hold_ops import assert_disjoint, load_prompt_ids
from hyp_lay import run_h_lay
from lay_fit import fitness_lay_detail, tip_row
from lay_ops import scale_flops_by_layers
from layer_exit import n_transformer_layers
from load_model import resolve_device
from matrix_common import REPO, ROOT, write_json
from run_formal_hdeck import formal_cfg as hdeck_formal_cfg
from student_model import count_params

LAM = 0.4


def formal_cfg() -> dict[str, Any]:
    base = hdeck_formal_cfg()
    base["out"] = REPO / "results/nano-lm/formal-hlay"
    base["ckpt_dir"] = REPO / "results/nano-lm/formal-hdeck-b4"
    base["early_dir"] = REPO / "results/nano-lm/formal-hearly"
    base["fit_prompts"] = ROOT / "prompts/fit_prompts.yaml"
    base["prompts"] = ROOT / "prompts/eval_prompts.yaml"
    base["lay_pop"] = 8
    base["lay_gens"] = 6
    return base


def _early_gene(early_dir: Path, seed: int) -> dict[str, Any]:
    path = early_dir / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing formal EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _texts(path: Path) -> list[str]:
    return [
        p["text"]
        for p in yaml.safe_load(path.read_text(encoding="utf-8"))["prompts"]
    ]


def _score_early(
    teacher, student, prompts: list[str], gene: dict, max_new: int, seed: int
) -> tuple[float, float, float]:
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    n_layers = n_transformer_layers(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, text in enumerate(prompts):
        result = decode_early(
            student,
            tok,
            text,
            n=int(gene["n"]),
            max_new_tokens=max_new,
            min_new=int(gene["min_new"]),
            conf_threshold=float(gene["conf_threshold"]),
            patience=int(gene["patience"]),
            temperature=float(gene["temperature"]),
            top_p=float(gene["top_p"]),
            seed=seed + i,
            device=device,
        )
        walls.append(result.wall_ms)
        ids = tok.encode(text, return_tensors="pt")
        scores.append(teacher_mean_logprob(teacher, ids, list(result.token_ids)))
        full = est_decode_flops(
            n_params=n_params,
            prompt_len=int(ids.shape[1]),
            n_new=len(result.token_ids),
            token_evals=result.token_evals,
        )
        scaled = scale_flops_by_layers(
            full,
            layer_evals=int(result.token_evals) * n_layers,
            token_evals=int(result.token_evals),
            n_layers=n_layers,
        )
        gflops.append(to_gflops(scaled))
    n = max(len(scores), 1)
    return sum(scores) / n, sum(walls) / n, sum(gflops) / n


def _run_seed(c: dict[str, Any], seed: int) -> list[dict[str, Any]]:
    ckpt = c["ckpt_dir"] / f"B2_seed{seed}.pt"
    if not ckpt.is_file():
        raise FileNotFoundError(f"missing shared B2 ckpt: {ckpt}")
    early = _early_gene(c["early_dir"], seed)
    meta = run_h_lay(
        student_ckpt=ckpt,
        teacher_id=c["teacher_id"],
        tokenizer_id=c["tokenizer_id"],
        prompts_path=c["fit_prompts"],
        eval_prompts_path=c["prompts"],
        cache_dir=c["cache"],
        pop_size=int(c["lay_pop"]),
        generations=int(c["lay_gens"]),
        max_new=int(c["max_new_fit"]),
        eval_max_new=int(c["max_new_eval"]),
        seed=seed,
        early_gene=early,
        lam=LAM,
        out_meta=c["out"] / f"HLAY_seed{seed}_train.json",
    )
    teacher, student = load_pair(
        ckpt, c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    prompts = _texts(c["prompts"])
    claim = seed + 7777
    max_new = int(c["max_new_eval"])
    lp_e, wall_e, gf_e = _score_early(
        teacher, student, prompts, early, max_new, claim
    )
    lp_l, wall_l, gf_l = fitness_lay_detail(
        meta["best_gene"],
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    gene = {**early, **meta["best_gene"]}
    n_p = len(prompts)
    row_e = tip_row("H-EARLY", f"HEARLY_lay_formal_seed{seed}", lp_e, wall_e, gf_e, seed, early)
    row_l = tip_row("H-LAY", f"HLAY_formal_seed{seed}", lp_l, wall_l, gf_l, seed, gene)
    row_e["n_prompts"] = n_p
    row_l["n_prompts"] = n_p
    write_json(c["out"] / f"HLAY_seed{seed}_eval.json", row_l)
    return [row_e, row_l]


def run_formal() -> int:
    c = formal_cfg()
    assert_disjoint(load_prompt_ids(c["fit_prompts"]), load_prompt_ids(c["prompts"]))
    device = resolve_device(True)
    c["out"].mkdir(parents=True, exist_ok=True)
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        rows.extend(_run_seed(c, seed))
        if device.type == "cuda":
            torch.cuda.empty_cache()
    write_json(
        c["out"] / "formal.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0, "lam": LAM},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(c["out"] / "formal.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(run_formal())
