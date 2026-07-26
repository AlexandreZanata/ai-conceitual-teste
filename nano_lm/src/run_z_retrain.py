"""Wave Z3 H-ZERR: retrain champion on error_bank.jsonl → models/zerr/."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import torch

from data_tiny import load_tokenizer
from eval_student import load_student_ckpt
from load_model import resolve_device
from matrix_common import REPO, eval_ckpt, matrix_cfg, write_json
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows
from zerr_ops import (
    DEFAULT_STEPS,
    HYPOTHESIS,
    STAG_TIP_LP,
    bank_qa_pairs,
    decide_hzerr,
)
from zerr_train import train_zerr

_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_OUT = REPO / "results/nano-lm/wave-z/models/zerr"


def _free_cuda(*objs: object) -> None:
    for obj in objs:
        del obj
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def run_zerr(
    *,
    seed: int = 0,
    steps: int = DEFAULT_STEPS,
    bank_path: Path | None = None,
    champ_root: Path | None = None,
    out_dir: Path | None = None,
) -> dict[str, Any]:
    """
    GIVEN champion ckpt + error bank (≥10 golds)
    WHEN tiny CE on Q→A only
    THEN write HZERR ckpt + gate story_lp vs STAG′−ε.
    """
    champ = Path(champ_root) if champ_root else _CHAMPION
    out = Path(out_dir) if out_dir else _OUT
    bank = Path(bank_path) if bank_path else _BANK
    recipe = json.loads((champ / "recipe.json").read_text(encoding="utf-8"))
    ckpt_in = champ / str(recipe["ckpt"])
    pairs = bank_qa_pairs(load_bank_rows(bank))
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-ZERR requires CUDA")
    tok = load_tokenizer(str(recipe["tokenizer_id"]), c["cache"])
    parent_ev = eval_ckpt(c, ckpt_in, int(seed), "champion-parent")
    parent_lp = float(parent_ev["teacher_mean_logprob"])
    student = load_student_ckpt(ckpt_in, tok, device)
    t0 = time.perf_counter()
    ckpt_out = out / f"HZERR_seed{int(seed)}.pt"
    try:
        train_meta = train_zerr(
            student=student,
            tok=tok,
            pairs=pairs,
            device=device,
            steps=int(steps),
            lr=float(c["lr"]),
            seed=int(seed),
            out_path=ckpt_out,
        )
    finally:
        _free_cuda(student)
    ev = eval_ckpt(c, ckpt_out, int(seed), HYPOTHESIS)
    story_lp = float(ev["teacher_mean_logprob"])
    decision = decide_hzerr(
        story_lp=story_lp,
        n_pairs=len(pairs),
        n_params=int(train_meta["params"]),
        parent_story_lp=parent_lp,
    )
    report = {
        "hypothesis": HYPOTHESIS,
        "stage": "Z3",
        "decision": decision,
        "story_lp": story_lp,
        "parent_story_lp": parent_lp,
        "stag_tip_lp": STAG_TIP_LP,
        "train": train_meta,
        "eval": {
            k: ev[k]
            for k in ("teacher_mean_logprob", "wall_ms", "family")
            if k in ev
        },
        "bank_path": str(bank),
        "ckpt_in": str(ckpt_in),
        "ckpt_out": str(ckpt_out),
        "elapsed_s": time.perf_counter() - t0,
        "parent_wrap": "champion-wrap-v0",
        "note": (
            "CE on error-bank golds only; no MIXD. Gate = parent−ε "
            "(Z0 B2 below tip STAG′). Z4 HITL verifies mean ≥ Z1+0.5."
        ),
    }
    write_json(out / f"HZERR_seed{int(seed)}_train.json", train_meta)
    # Ask-compatible recipe card (same EARLY gene; new ckpt).
    zerr_recipe = dict(recipe)
    zerr_recipe["recipe_id"] = "zerr-qpfb2-v0"
    zerr_recipe["family"] = HYPOTHESIS
    zerr_recipe["ckpt"] = f"HZERR_seed{int(seed)}.pt"
    gene_rel = str(recipe["early_gene"])
    gene_src = champ / gene_rel
    gene_dst = out / gene_rel
    gene_dst.parent.mkdir(parents=True, exist_ok=True)
    if gene_src.is_file() and not gene_dst.is_file():
        gene_dst.write_bytes(gene_src.read_bytes())
    write_json(out / "recipe.json", zerr_recipe)
    write_json(out / "MANIFEST.json", report)
    write_json(REPO / "results/nano-lm/wave-z/z3_zerr_summary.json", report)
    return report


def main() -> int:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    ap.add_argument("--bank", type=Path, default=_BANK)
    ap.add_argument("--champ", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_OUT)
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        report = run_zerr(
            seed=int(args.seed),
            steps=int(args.steps),
            bank_path=args.bank,
            champ_root=args.champ,
            out_dir=args.out,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    report["ok"] = True
    report["cpu_threads"] = threads
    print(json.dumps(report))
    return 0 if str(report["decision"]).startswith("PROMOTE") else 3


if __name__ == "__main__":
    raise SystemExit(main())
