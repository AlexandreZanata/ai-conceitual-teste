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
from modeui_ops import attach_modeui
from qt_quant import quantize_student_int8
from tipd_pair import tune_cpu_threads
from z_recipe import validate_recipe
from z_wrap import (
    WRAP_ID,
    build_fewshot_prompt,
    default_wrap_card,
    load_bank_rows,
    lookup_gold,
    wrap_ask_gene,
)

_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"


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


def _load_raw_gene(root: Path, recipe: dict[str, Any]) -> dict[str, Any]:
    path = root / str(recipe["early_gene"])
    gene = json.loads(path.read_text(encoding="utf-8")).get("best_gene")
    if not isinstance(gene, dict):
        raise ValueError(f"missing best_gene: {path}")
    return gene


def _baseline_gene(raw: dict[str, Any]) -> dict[str, Any]:
    return clamp_early_gene({**raw, "n": 1, "temperature": 1e-6})


def _ensure_wrap_card(root: Path) -> None:
    path = root / "wrap.json"
    if not path.is_file():
        write_json(path, default_wrap_card())


def _lookup_payload(
    recipe: dict[str, Any],
    question: str,
    gold: str,
    seed: int,
    *,
    mode: str = "WRAP_LOOKUP",
) -> dict[str, Any]:
    return {
        "recipe_id": recipe["recipe_id"],
        "family": recipe["family"],
        "question": question,
        "completion": gold,
        "wall_ms": 0.0,
        "n_new": 0,
        "seed": int(seed),
        "mode": mode,
        "elapsed_s": 0.0,
        "wrap_id": WRAP_ID,
    }


def _decode_one(
    *,
    qt: Any,
    tok: Any,
    recipe: dict[str, Any],
    gene: dict[str, Any],
    prompt: str,
    question: str,
    seed: int,
    device: torch.device,
    mode: str,
    max_new: int,
    temperature: float,
) -> dict[str, Any]:
    t0 = time.perf_counter()
    result = decode_early(
        qt,
        tok,
        prompt,
        n=1,
        max_new_tokens=int(max_new),
        min_new=int(gene["min_new"]),
        conf_threshold=float(gene["conf_threshold"]),
        patience=int(gene["patience"]),
        temperature=float(temperature),
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
        "mode": mode,
        "elapsed_s": time.perf_counter() - t0,
        "wrap_id": WRAP_ID if mode.startswith("WRAP") else None,
    }


def _finalize_ask_payload(
    payload: dict[str, Any], *, abstain: bool
) -> dict[str, Any]:
    """
    GIVEN raw ask payload
    WHEN optional refuse-junk gate is on (default product path)
    THEN ABSTAIN/NO_ANSWER sticks with visible modeui_line; else MODEUI attach.
    """
    out = dict(payload)
    if abstain:
        from abstain_ops import apply_abstain

        out = apply_abstain(out)
    if bool(out.get("abstained")) or str(out.get("product_mode", "")) == "ABSTAIN":
        from modeui_ops import format_modeui_line

        raw = str(out.get("mode", "") or "")
        out["product_mode"] = "ABSTAIN"
        out["modeui_line"] = format_modeui_line(
            product_mode="ABSTAIN",
            wall_ms=float(out.get("wall_ms") or 0.0),
            n_new=int(out.get("n_new") or 0),
            raw_mode=raw,
        )
        return out
    return attach_modeui(out)


def ask_once(
    *,
    question: str,
    root: Path | None = None,
    seed: int = 0,
    wrap: bool = False,
    semwrap: bool = False,
    askfast: bool = False,
    bank_path: Path | None = None,
    curated_root: Path | None = None,
    ask_cache: Any | None = None,
    abstain: bool = True,
) -> dict[str, Any]:
    """
    GIVEN exported champion + question
    WHEN decoding QT∘EARLY n=1 (optional wrap / SEMWRAP / ASKFAST)
    THEN return completion + wall_ms + recipe_id; junk DECODE → ABSTAIN
         on the default path (abstain=True).
    """
    return ask_many(
        questions=[question],
        root=root,
        seed=seed,
        wrap=wrap,
        semwrap=semwrap,
        askfast=askfast,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=ask_cache,
        abstain=abstain,
    )[0]


def _fill_lookups(
    questions: list[str],
    *,
    recipe: dict[str, Any],
    bank: list[dict[str, Any]],
    seed: int,
    wrap: bool,
    semwrap: bool,
    curated_root: Path | None,
    ask_cache: Any | None,
) -> tuple[list[dict[str, Any] | None], list[tuple[int, str]]]:
    out: list[dict[str, Any] | None] = [None] * len(questions)
    pending: list[tuple[int, str]] = []
    for i, q in enumerate(questions):
        if ask_cache is not None:
            from askfast_ops import merge_cache_payload

            hit = ask_cache.get(q)
            if hit is not None:
                out[i] = merge_cache_payload(hit, question=q, seed=seed)
                out[i]["recipe_id"] = out[i].get("recipe_id") or recipe.get(
                    "recipe_id"
                )
                out[i]["family"] = out[i].get("family") or recipe.get("family")
                continue
        if wrap or semwrap:
            gold = lookup_gold(q, bank)
            if gold is not None:
                out[i] = _lookup_payload(recipe, q, gold, seed)
                continue
            if semwrap:
                from semwrap_ops import semantic_lookup

                fuzzy, meta = semantic_lookup(
                    q, bank, curated_root=curated_root
                )
                if fuzzy is not None:
                    payload = _lookup_payload(
                        recipe, q, fuzzy, seed, mode="SEMWRAP_LOOKUP"
                    )
                    payload["semwrap"] = meta
                    out[i] = payload
                    continue
                if str(meta.get("kind")) == "REJECT_NEAR_MISS":
                    # Production refuse (AU1) — same path humans use.
                    payload = _lookup_payload(
                        recipe, q, "NO_ANSWER", seed, mode="NO_ANSWER"
                    )
                    payload["semwrap"] = meta
                    payload["abstained"] = True
                    payload["product_mode"] = "ABSTAIN"
                    out[i] = payload
                    continue
        pending.append((i, q))
    return out, pending


def ask_many(
    *,
    questions: list[str],
    root: Path | None = None,
    seed: int = 0,
    wrap: bool = False,
    semwrap: bool = False,
    askfast: bool = False,
    bank_path: Path | None = None,
    curated_root: Path | None = None,
    ask_cache: Any | None = None,
    abstain: bool = True,
) -> list[dict[str, Any]]:
    """
    GIVEN exported champion + N questions
    WHEN one CUDA load (ASKFAST: SEMWRAP + QT + completion cache)
    THEN return N payloads in order; default path applies refuse-junk ABSTAIN.
    """
    if not questions:
        raise ValueError("questions must be non-empty")
    champ = Path(root) if root is not None else _CHAMPION
    recipe = _load_recipe(champ)
    raw = _load_raw_gene(champ, recipe)
    bank = load_bank_rows(Path(bank_path) if bank_path else _BANK)
    use_sem = bool(semwrap or askfast)
    use_wrap = bool(wrap or use_sem)
    cache = ask_cache
    if askfast and cache is None:
        from askfast_ops import AskCompletionCache

        cache = AskCompletionCache()
    if use_wrap:
        _ensure_wrap_card(champ)
        gene = wrap_ask_gene(raw)
        temperature = float(gene["temperature"])
        max_new = 64
        mode_decode = "WRAP_DECODE"
    else:
        gene = _baseline_gene(raw)
        temperature = 1e-6
        max_new = int(recipe["max_new"])
        mode_decode = "QT+EARLY n=1"

    out, pending = _fill_lookups(
        questions,
        recipe=recipe,
        bank=bank,
        seed=seed,
        wrap=use_wrap,
        semwrap=use_sem,
        curated_root=curated_root,
        ask_cache=cache,
    )
    if not pending:
        payloads = [p for p in out if p is not None]
        if cache is not None:
            for q, p in zip(questions, payloads, strict=True):
                if not p.get("cache_hit"):
                    cache.put(q, p)
        return [
            _finalize_ask_payload(dict(p), abstain=abstain) for p in payloads
        ]

    device = resolve_device(True)
    if device.type != "cuda":
        raise RuntimeError("Wave Z ask requires CUDA")
    tok = load_tokenizer(str(recipe["tokenizer_id"]), matrix_cfg()["cache"])
    student = load_student_ckpt(champ / str(recipe["ckpt"]), tok, device)
    qt = quantize_student_int8(student)  # type: ignore[arg-type]
    qt.to(device)
    try:
        for i, q in pending:
            prompt = build_fewshot_prompt(q, bank, k=3) if use_wrap else q
            out[i] = _decode_one(
                qt=qt,
                tok=tok,
                recipe=recipe,
                gene=gene,
                prompt=prompt,
                question=q,
                seed=seed,
                device=device,
                mode=mode_decode,
                max_new=max_new,
                temperature=temperature,
            )
    finally:
        _free_cuda(qt, student)
    payloads = [p for p in out if p is not None]
    if cache is not None:
        for q, p in zip(questions, payloads, strict=True):
            if not p.get("cache_hit"):
                cache.put(q, p)
    return [_finalize_ask_payload(dict(p), abstain=abstain) for p in payloads]


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
    ap.add_argument("--wrap", action="store_true")
    ap.add_argument("--semwrap", action="store_true")
    ap.add_argument("--askfast", action="store_true")
    ap.add_argument("--bank", type=Path, default=_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=None)
    args = ap.parse_args()
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        payload = ask_once(
            question=str(args.question),
            root=args.root,
            seed=int(args.seed),
            wrap=bool(args.wrap),
            semwrap=bool(args.semwrap),
            askfast=bool(args.askfast),
            bank_path=args.bank,
            curated_root=REPO / "nano_lm/data/curated",
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
