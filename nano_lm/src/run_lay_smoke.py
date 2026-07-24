"""Smoke H-LAY: layer early-exit under frozen H-EARLY tip vs tip control."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from decode_early import decode_early
from eval_decode import load_pair
from eval_student import teacher_mean_logprob
from flop_ops import est_decode_flops, to_gflops
from flop_score import load_prompts
from hyp_lay import run_h_lay
from lay_fit import fitness_lay_detail, tip_row
from lay_ops import scale_flops_by_layers
from layer_exit import n_transformer_layers
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json
from student_model import count_params

LAM = 0.4


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _score_early(
    teacher, student, prompts: list[dict], gene: dict, max_new: int, seed: int
) -> tuple[float, float, float]:
    tok = teacher.tokenizer
    device = teacher.device
    n_params = count_params(student)
    n_layers = n_transformer_layers(student)
    scores: list[float] = []
    walls: list[float] = []
    gflops: list[float] = []
    for i, p in enumerate(prompts):
        result = decode_early(
            student,
            tok,
            p["text"],
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
        ids = tok.encode(p["text"], return_tensors="pt")
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


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; smoke will be slow/CPU", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = load_prompts(c["prompts"])
    prompt_texts = [p["text"] for p in prompts]
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        meta = run_h_lay(
            student_ckpt=out / f"B2_seed{seed}.pt",
            teacher_id=c["teacher_id"],
            tokenizer_id=c["tokenizer_id"],
            prompts_path=c["prompts"],
            cache_dir=c["cache"],
            pop_size=4,
            generations=2,
            max_new=min(16, max_new),
            eval_max_new=max_new,
            seed=seed,
            early_gene=early,
            lam=LAM,
            out_meta=out / f"HLAY_seed{seed}_train.json",
        )
        # Claim scores after search (shared warm GPU); tip then LAY.
        teacher, student = load_pair(
            out / f"B2_seed{seed}.pt",
            c["teacher_id"],
            c["tokenizer_id"],
            c["cache"],
        )
        claim_seed = seed + 7777
        lp_e, wall_e, gf_e = _score_early(
            teacher, student, prompts, early, max_new, claim_seed
        )
        rows.append(
            tip_row(
                "H-EARLY", f"HEARLY_lay_seed{seed}", lp_e, wall_e, gf_e, seed, early
            )
        )
        lp_l, wall_l, gf_l = fitness_lay_detail(
            meta["best_gene"],
            early,
            teacher=teacher,
            student=student,
            prompts=prompt_texts,
            max_new=max_new,
            seed=claim_seed,
        )
        gene = {**early, **meta["best_gene"]}
        row = tip_row("H-LAY", f"HLAY_seed{seed}", lp_l, wall_l, gf_l, seed, gene)
        write_json(out / f"HLAY_seed{seed}_eval.json", row)
        rows.append(row)
    write_json(
        out / "lay_smoke.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "lay_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
