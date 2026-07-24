"""Smoke H-AMP: CUDA AMP train + autocast decode vs frozen H-EARLY tip."""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path
from typing import Any

from amp_fit import _row, score_early_amp, score_early_fp32
from amp_train import train_kd_amp
from decode_early import decode_early
from eval_decode import load_pair
from flop_score import load_prompts
from load_model import resolve_device
from matrix_common import matrix_cfg, write_json

AMP_KIND = "bf16"
TRAIN_STEPS = 20


def _early_gene(out: Path, seed: int) -> dict[str, Any]:
    path = out / f"HEARLY_seed{seed}_train.json"
    if not path.is_file():
        raise FileNotFoundError(f"missing EARLY tip: {path}")
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"EARLY missing best_gene: {path}")
    return gene


def _warmup(student, tok, device, gene: dict[str, Any]) -> None:
    decode_early(
        student,
        tok,
        "Once upon a time",
        n=1,
        max_new_tokens=4,
        min_new=4,
        conf_threshold=0.99,
        patience=3,
        temperature=float(gene["temperature"]),
        top_p=float(gene["top_p"]),
        seed=0,
        device=device,
    )


def _train_amp(c: dict[str, Any], out: Path, seed: int, device) -> None:
    meta = train_kd_amp(
        teacher_id=c["teacher_id"],
        steps=TRAIN_STEPS,
        batch_size=int(c["batch_size"]),
        seq_len=int(c["seq_len"]),
        max_examples=int(c["max_examples"]),
        lr=float(c["lr"]),
        seed=seed,
        temperature=2.0,
        alpha=0.5,
        tokenizer_id=c["tokenizer_id"],
        cache_dir=c["cache"],
        device=device,
        out_path=out / f"HAMP_seed{seed}_train.pt",
        amp_kind=AMP_KIND,
    )
    write_json(out / f"HAMP_seed{seed}_train.json", meta)


def _claim_seed(
    c: dict[str, Any],
    out: Path,
    seed: int,
    early: dict[str, Any],
    prompts: list[str],
    max_new: int,
) -> list[dict[str, Any]]:
    teacher, student = load_pair(
        out / f"B2_seed{seed}.pt", c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    _warmup(student, teacher.tokenizer, teacher.device, early)
    claim = seed + 7777
    lp_e, wall_e, gf_e = score_early_fp32(
        early,
        teacher=teacher,
        student=student,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
    )
    _, student_amp = load_pair(
        out / f"B2_seed{seed}.pt", c["teacher_id"], c["tokenizer_id"], c["cache"]
    )
    lp_a, wall_a, gf_a, dtype_s = score_early_amp(
        early,
        teacher=teacher,
        student=student_amp,
        prompts=prompts,
        max_new=max_new,
        seed=claim,
        amp_kind=AMP_KIND,
    )
    row = _row(
        "H-AMP",
        f"HAMP_seed{seed}",
        lp_a,
        wall_a,
        gf_a,
        seed,
        {
            "amp_kind": AMP_KIND,
            "dtype": dtype_s,
            "train_steps": TRAIN_STEPS,
            "best_gene": early,
        },
    )
    write_json(out / f"HAMP_seed{seed}_eval.json", row)
    return [
        _row("H-EARLY", f"HEARLY_amp_seed{seed}", lp_e, wall_e, gf_e, seed),
        row,
    ]


def main() -> int:
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        print("WARN: CUDA unavailable; AMP falls back to fp32", file=sys.stderr)
    out: Path = c["out"]
    out.mkdir(parents=True, exist_ok=True)
    prompts = [p["text"] for p in load_prompts(c["prompts"])]
    max_new = int(c["max_new_eval"])
    rows: list[dict[str, Any]] = []
    t0 = time.perf_counter()
    for seed in c["seeds"]:
        early = _early_gene(out, seed)
        _train_amp(c, out, seed, device)
        rows.extend(_claim_seed(c, out, seed, early, prompts, max_new))
    write_json(
        out / "amp_smoke.json",
        {"rows": rows, "wall_s": time.perf_counter() - t0, "amp_kind": AMP_KIND},
    )
    print(json.dumps({"n_rows": len(rows), "out": str(out / "amp_smoke.json")}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
