"""Wave Z ask: one completion from exported champion (QT + EARLY n=1)."""

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
from decode_early import decode_early
from early_ops import clamp_early_gene
from eval_student import load_student_ckpt
from load_model import resolve_device
from matrix_common import REPO, matrix_cfg, write_json
from qt_quant import quantize_student_int8
from tipd_pair import tune_cpu_threads
from z_recipe import validate_recipe

_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"


def _free_cuda(*objs: object) -> None:
    for obj in objs:
        del obj
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
        torch.cuda.synchronize()


def _load_recipe(root: Path) -> dict[str, Any]:
    path = root / "recipe.json"
    recipe = json.loads(path.read_text(encoding="utf-8"))
    errs = validate_recipe(recipe)
    if errs:
        raise ValueError("bad recipe: " + "; ".join(errs))
    return recipe


def _load_gene(root: Path, recipe: dict[str, Any]) -> dict[str, Any]:
    path = root / str(recipe["early_gene"])
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return clamp_early_gene({**gene, "n": 1, "temperature": 1e-6})


def _decode_one(
    *,
    qt: Any,
    tok: Any,
    recipe: dict[str, Any],
    gene: dict[str, Any],
    question: str,
    seed: int,
    device: torch.device,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    result = decode_early(
        qt,
        tok,
        question,
        n=1,
        max_new_tokens=int(recipe["max_new"]),
        min_new=int(gene["min_new"]),
        conf_threshold=float(gene["conf_threshold"]),
        patience=int(gene["patience"]),
        temperature=1e-6,
        top_p=float(gene["top_p"]),
        seed=int(seed),
        device=device,
    )
    return {
        "recipe_id": recipe["recipe_id"],
        "family": recipe["family"],
        "question": question,
        "completion": result.text,
        "wall_ms": float(result.wall_ms),
        "n_new": len(result.token_ids),
        "seed": int(seed),
        "mode": "QT+EARLY n=1",
        "elapsed_s": time.perf_counter() - t0,
    }


def ask_once(
    *,
    question: str,
    root: Path | None = None,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN exported champion + question
    WHEN decoding QT∘EARLY n=1
    THEN return completion + wall_ms + recipe_id (no teacher self-grade).
    """
    return ask_many(questions=[question], root=root, seed=seed)[0]


def ask_many(
    *,
    questions: list[str],
    root: Path | None = None,
    seed: int = 0,
) -> list[dict[str, Any]]:
    """
    GIVEN exported champion + N questions
    WHEN decoding QT∘EARLY n=1 with one model load
    THEN return N completion payloads (warm GPU; no teacher).
    """
    if not questions:
        raise ValueError("questions must be non-empty")
    champ = Path(root) if root is not None else _CHAMPION
    recipe = _load_recipe(champ)
    gene = _load_gene(champ, recipe)
    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("Wave Z ask requires CUDA")
    cache = matrix_cfg()["cache"]
    tok = load_tokenizer(str(recipe["tokenizer_id"]), cache)
    student = load_student_ckpt(champ / str(recipe["ckpt"]), tok, device)
    qt = quantize_student_int8(student)  # type: ignore[arg-type]
    qt.to(device)
    out: list[dict[str, Any]] = []
    try:
        for q in questions:
            out.append(
                _decode_one(
                    qt=qt,
                    tok=tok,
                    recipe=recipe,
                    gene=gene,
                    question=q,
                    seed=seed,
                    device=device,
                )
            )
    finally:
        _free_cuda(qt, student)
    return out


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
    ap.add_argument("--question", required=True)
    ap.add_argument("--trial", default="")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument(
        "--root",
        type=Path,
        default=_CHAMPION,
    )
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        payload = ask_once(
            question=str(args.question), root=args.root, seed=int(args.seed)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    payload["ok"] = True
    payload["cpu_threads"] = threads
    if args.trial:
        payload["trial_id"] = str(args.trial)
    print(json.dumps(payload))
    if args.out is not None:
        write_json(args.out, payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
