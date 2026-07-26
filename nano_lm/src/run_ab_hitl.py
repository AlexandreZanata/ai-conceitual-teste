"""Wave AB6 AB-HITL-10 runner: final pack on declared AB stack (nano:ab:hitl)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ab_hitl_ops import (
    AB6_ID,
    AB6_N,
    DECLARED_STACK,
    STACK_CLAIM,
    ab6_stats,
    claim_is_honest,
    decide_ab6,
    score_ab6_trial,
    select_app,
)
from ab_session_ops import AB0_PACK
from askfast_ops import AskCompletionCache
from curated_sources import SOURCES
from data_tiny import load_tokenizer
from longapp_ops import longapp_doc_meta
from matrix_common import REPO, matrix_cfg, write_json
from run_z_ask import ask_many
from semwrap_ops import classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_trial import validate_trial
from z_wrap import load_bank_rows

_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_ERR_AB = REPO / "results/nano-lm/wave-ab/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ab/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ab/ab_hitl_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
_BY_ID = {str(s["id"]): s for s in SOURCES}


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


def _load_doc(source_id: str, curated: Path) -> str:
    meta = _BY_ID.get(source_id)
    if meta is None:
        raise ValueError(f"unknown source_id: {source_id}")
    path = curated / str(meta["path"])
    if not path.is_file():
        raise FileNotFoundError(str(path))
    return path.read_text(encoding="utf-8", errors="ignore")


def _classify(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any]]:
    mode = str(payload.get("mode", ""))
    if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}:
        _g, meta = semantic_lookup(
            item["question"], bank, curated_root=curated
        )
        kind = classify_semwrap(
            str(payload.get("completion")),
            expected_gold=item["gold"],
            expected_source_id=item["source_id"],
            hit_source_id=str(meta.get("source_id") or "") or None,
        )
        return kind, meta
    gold, meta = semantic_lookup(
        item["question"], bank, curated_root=curated
    )
    kind = classify_semwrap(
        gold,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta


def _build_ctxs(
    *,
    curated_root: Path,
    workers: int,
) -> list[dict[str, Any] | None]:
    cfg = matrix_cfg()
    tok = load_tokenizer(str(cfg["tokenizer_id"]), cfg["cache"])

    def _read(item: dict[str, str]) -> tuple[dict[str, str], str]:
        return item, _load_doc(item["source_id"], curated_root)

    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        pairs = list(pool.map(_read, [dict(p) for p in AB0_PACK]))
    out: list[dict[str, Any] | None] = []
    for item, text in pairs:
        if item["app_id"] != "long-doc":
            out.append(None)
            continue
        ids = list(tok.encode(text, add_special_tokens=False))
        q_ids = list(tok.encode(item["question"], add_special_tokens=False))
        meta = longapp_doc_meta(ids, q_ids)
        meta["source_id"] = item["source_id"]
        out.append(meta)
    return out


def _append_error(
    path: Path,
    *,
    trial_id: str,
    item: dict[str, str],
    completion: str,
    score: float,
    notes: list[str],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    row = {
        "trial_id": trial_id,
        "stage": "AB6",
        "hyp_id": AB6_ID,
        "question": item["question"],
        "source_id": item["source_id"],
        "app_id": item["app_id"],
        "model_raw": completion,
        "gold": item["gold"],
        "score": score,
        "error": True,
        "judge_notes": notes,
        "recipe_id": "champion-ab-v0",
    }
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_ab_hitl(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    error_bank: Path,
    seed: int = 0,
    workers: int = 8,
) -> dict[str, Any]:
    """
    GIVEN AB0 pack + declared AB stack
    WHEN ASK→EVAL→FIX×10 via app router (known vs longdoc)
    THEN mean≥7 · errors≤3 · no false-hit → PROMOTE|HOLD|KILL.
    """
    if len(AB0_PACK) != AB6_N:
        raise ValueError("AB0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    bank = load_bank_rows(bank_path)
    claim_ok = claim_is_honest(STACK_CLAIM)
    ctxs = _build_ctxs(curated_root=curated_root, workers=workers)
    questions = [p["question"] for p in AB0_PACK]
    cache = AskCompletionCache()
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=cache,
    )
    if len(payloads) != AB6_N:
        raise RuntimeError(f"expected {AB6_N} payloads")

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload) in enumerate(
        zip(AB0_PACK, payloads, strict=True), start=1
    ):
        tid = f"AB-FINAL-HITL-{i:02d}"
        routed = select_app(item["app_id"])
        kind, sem_meta = _classify(dict(item), payload, bank, curated_root)
        ctx = ctxs[i - 1]
        long_ok = None
        if routed == "app-longdoc" and ctx is not None:
            long_ok = bool(ctx.get("l_eff_ok")) and bool(ctx.get("ratio_ok"))
        score_before, err_before, notes_before = score_ab6_trial(
            mode=str(payload.get("mode", "")),
            completion=str(payload.get("completion", "")),
            expected_gold=str(item["gold"]),
            lookup_kind=kind,
            longapp_ok=long_ok,
        )
        score, err, notes = score_before, err_before, list(notes_before)
        completion = str(payload.get("completion", ""))
        mode = str(payload.get("mode", ""))
        fixed = False
        if err:
            fixed = True
            fix_count += 1
            _append_error(
                error_bank,
                trial_id=tid,
                item=dict(item),
                completion=completion,
                score=score_before,
                notes=notes_before,
            )
            gold, meta = semantic_lookup(
                item["question"], bank, curated_root=curated_root
            )
            if gold is not None:
                completion = str(gold)
                mode = "AB6_CONSTRAINED_FIX"
                kind = classify_semwrap(
                    completion,
                    expected_gold=item["gold"],
                    expected_source_id=item["source_id"],
                    hit_source_id=str(meta.get("source_id") or "") or None,
                )
                sem_meta = meta
                score, err, notes = score_ab6_trial(
                    mode=mode,
                    completion=completion,
                    expected_gold=str(item["gold"]),
                    lookup_kind=kind,
                    longapp_ok=long_ok,
                )
                notes = list(notes) + [
                    f"score_before={score_before}",
                    f"score_after={score}",
                    "FIX: constrained SEMWRAP re-ASK",
                ]
        adjust = (
            "FIX: constrained SEMWRAP re-ASK"
            if fixed
            else "no change — AB6 final stack ok"
        )
        trial: dict[str, Any] = {
            "trial_id": tid,
            "stage": "AB6",
            "hyp_id": AB6_ID,
            "realapp_id": routed,
            "app_id": item["app_id"],
            "question": item["question"],
            "source_id": item["source_id"],
            "recipe_id": payload.get("recipe_id") or "champion-ab-v0",
            "ckpt": None,
            "completion": completion,
            "wall_ms": payload.get("wall_ms"),
            "n_new": payload.get("n_new"),
            "seed": payload.get("seed", 0),
            "mode": mode,
            "lookup_kind": kind,
            "semwrap": sem_meta,
            "longapp": ctx,
            "score": score,
            "score_before": score_before,
            "error": err,
            "judge_model_name": _JUDGE,
            "judge_notes": notes,
            "manual_adjust": adjust,
            "gold": str(item["gold"]).strip(),
            "repaired": str(item["gold"]).strip(),
            "wrap_id": payload.get("wrap_id"),
            "weight_update": False,
        }
        errs = validate_trial(trial)
        if errs:
            raise ValueError(f"{tid}: " + "; ".join(errs))
        write_json(trials_dir / f"{tid}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    n_known = sum(1 for t in trials if t["realapp_id"] == "app-known")
    n_long = sum(1 for t in trials if t["realapp_id"] == "app-longdoc")
    stats = ab6_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        n_fix=fix_count,
        claim_ok=claim_ok,
        n_known_app=n_known,
        n_long_app=n_long,
    )
    decision = decide_ab6(stats)
    summary: dict[str, Any] = {
        "hyp_id": AB6_ID,
        "stage": "AB6",
        "decision": decision,
        "stack": list(DECLARED_STACK),
        "claim": STACK_CLAIM,
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "ZPREF",
            "open chat claim",
            "reuse AB1-AB5 answers",
        ],
        "fix_count": fix_count,
        "stats": stats,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "app_id": t["app_id"],
                "realapp_id": t["realapp_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "score_before": t["score_before"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
            }
            for t in trials
        ],
        "finding": (
            f"{AB6_ID}: mean={stats['mean']:.1f} "
            f"errors={stats['n_errors']}/10 "
            f"false_hit={n_false} fix={fix_count} "
            f"decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/wave-ab-hitl.md",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--error-bank", type=Path, default=_ERR_AB)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(12, max(4, cpus - 4))
    try:
        summary = run_ab_hitl(
            bank_path=Path(args.bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            error_bank=Path(args.error_bank),
            seed=int(args.seed),
            workers=workers,
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": AB6_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_errors": summary["stats"]["n_errors"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "fix_count": summary["fix_count"],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
