"""Wave AA3 H-ZPREF: preference retrain gold≻raw → models/zpref/ (nano:zpref)."""

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
from run_z_ask import ask_once
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows
from zpref_ops import (
    DEFAULT_STEPS,
    HYPOTHESIS,
    STAG_TIP_LP,
    bank_pref_pairs,
    decide_hzpref,
)
from zpref_train import train_zpref

_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_OUT = REPO / "results/nano-lm/wave-aa/models/zpref"
_SUMMARY = REPO / "results/nano-lm/wave-aa/zpref_summary.json"
_VERIFY_Q = (
    "Write a short Python function named add that returns the sum of two integers a and b."
)


def _free_cuda(*objs: object) -> None:
    for obj in objs:
        del obj
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def _clear_proxy() -> None:
    for key in (
        "http_proxy",
        "https_proxy",
        "HTTP_PROXY",
        "HTTPS_PROXY",
        "ALL_PROXY",
        "all_proxy",
    ):
        os.environ.pop(key, None)


def _copy_gene(champ: Path, out: Path, gene_rel: str) -> None:
    src = champ / gene_rel
    dst = out / gene_rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    if src.is_file() and not dst.is_file():
        dst.write_bytes(src.read_bytes())


def _wrap_verify(root: Path, bank: Path) -> dict[str, Any]:
    """Z-HITL smoke: known-ask wrap must still LOOKUP after preference train."""
    payload = ask_once(
        question=_VERIFY_Q, root=root, seed=0, wrap=True, bank_path=bank
    )
    ok = str(payload.get("mode")) == "WRAP_LOOKUP" and bool(
        str(payload.get("completion", "")).strip()
    )
    return {
        "ok": ok,
        "mode": payload.get("mode"),
        "completion_head": str(payload.get("completion", ""))[:80],
        "question": _VERIFY_Q,
    }


def run_zpref(
    *,
    seed: int = 0,
    steps: int = DEFAULT_STEPS,
    bank_path: Path | None = None,
    champ_root: Path | None = None,
    out_dir: Path | None = None,
    summary_path: Path | None = None,
) -> dict[str, Any]:
    """
    GIVEN champion + bank≥20
    WHEN rank-prefer gold≻raw then story eval + wrap verify
    THEN write zpref ckpt + PROMOTE|KILL.
    """
    champ = Path(champ_root) if champ_root else _CHAMPION
    out = Path(out_dir) if out_dir else _OUT
    bank = Path(bank_path) if bank_path else _BANK
    summ = Path(summary_path) if summary_path else _SUMMARY
    recipe = json.loads((champ / "recipe.json").read_text(encoding="utf-8"))
    ckpt_in = champ / str(recipe["ckpt"])
    rows = load_bank_rows(bank)
    pairs = bank_pref_pairs(rows)
    c = matrix_cfg()
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("H-ZPREF requires CUDA")
    tok = load_tokenizer(str(recipe["tokenizer_id"]), c["cache"])
    parent_ev = eval_ckpt(c, ckpt_in, int(seed), "champion-parent")
    parent_lp = float(parent_ev["teacher_mean_logprob"])
    student = load_student_ckpt(ckpt_in, tok, device)
    t0 = time.perf_counter()
    ckpt_out = out / f"HZPREF_seed{int(seed)}.pt"
    try:
        train_meta = train_zpref(
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

    zpref_recipe = dict(recipe)
    zpref_recipe["recipe_id"] = "zpref-qpfb2-v0"
    zpref_recipe["family"] = HYPOTHESIS
    zpref_recipe["ckpt"] = f"HZPREF_seed{int(seed)}.pt"
    out.mkdir(parents=True, exist_ok=True)
    _copy_gene(champ, out, str(recipe["early_gene"]))
    write_json(out / "recipe.json", zpref_recipe)
    wrap_card = champ / "wrap.json"
    if wrap_card.is_file():
        (out / "wrap.json").write_bytes(wrap_card.read_bytes())

    hitl = _wrap_verify(out, bank)
    decision = decide_hzpref(
        story_lp=story_lp,
        n_pairs=len(pairs),
        n_bank_rows=len(rows),
        n_params=int(train_meta["params"]),
        parent_story_lp=parent_lp,
        wrap_ok=bool(hitl["ok"]),
    )
    report: dict[str, Any] = {
        "hypothesis": HYPOTHESIS,
        "stage": "AA3",
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
        "bank_rows": len(rows),
        "n_pref_pairs": len(pairs),
        "ckpt_in": str(ckpt_in),
        "ckpt_out": str(ckpt_out),
        "hitl_wrap_verify": hitl,
        "elapsed_s": time.perf_counter() - t0,
        "parent_wrap": "champion-wrap-v0",
        "note": (
            "Rank prefer gold≻raw (........ fallback); no MIXD. "
            "Gate = parent−ε + wrap LOOKUP verify. Not a chat LM claim."
        ),
    }
    write_json(out / f"HZPREF_seed{int(seed)}_train.json", train_meta)
    write_json(out / "MANIFEST.json", report)
    write_json(summ, report)
    return report


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--steps", type=int, default=DEFAULT_STEPS)
    ap.add_argument("--bank", type=Path, default=_BANK)
    ap.add_argument("--champ", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--summary", type=Path, default=_SUMMARY)
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        report = run_zpref(
            seed=int(args.seed),
            steps=int(args.steps),
            bank_path=args.bank,
            champ_root=args.champ,
            out_dir=args.out,
            summary_path=args.summary,
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
