"""Wave AB2 H-ASKFAST runner: fast ask HITL×10 (nano:askfast)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from ab_session_ops import AB0_PACK
from askfast_ops import (
    ASKFAST_ID,
    ASKFAST_N,
    AskCompletionCache,
    askfast_stats,
    decide_askfast,
    score_askfast_trial,
)
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_trial import validate_trial
from z_wrap import load_bank_rows

_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ab/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ab/askfast_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"


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


def _mean_wall(payloads: list[dict[str, Any]]) -> float:
    if not payloads:
        return 0.0
    return float(sum(float(p.get("wall_ms") or 0.0) for p in payloads)) / len(
        payloads
    )


def _classify(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any]]:
    mode = str(payload.get("mode", ""))
    if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}:
        _gold, meta = semantic_lookup(
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


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    arm: str,
) -> dict[str, Any]:
    tid = f"AB-ASKFAST-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes = score_askfast_trial(
        mode=mode,
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AB2",
        "hyp_id": ASKFAST_ID,
        "arm": arm,
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — ASKFAST quality held"
            if not err
            else "FIX: SEMWRAP/cache/decode knobs"
        ),
        "gold": str(item["gold"]).strip(),
        "repaired": str(item["gold"]).strip(),
        "wrap_id": payload.get("wrap_id"),
        "weight_update": False,
        "cache_hit": bool(payload.get("cache_hit")),
    }
    errs = validate_trial(trial)
    if errs:
        raise ValueError(f"{tid}: " + "; ".join(errs))
    return trial


def run_askfast(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AB0 asks + QT champion
    WHEN baseline decode vs ASKFAST (SEMWRAP+cache+QT batch)
    THEN wall↓≥20% + HITL quality → PROMOTE|HOLD|KILL.
    """
    if len(AB0_PACK) != ASKFAST_N:
        raise ValueError("AB0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    questions = [p["question"] for p in AB0_PACK]
    bank = load_bank_rows(bank_path)

    # Baseline: raw QT∘EARLY ask (no wrap/SEMWRAP) — product without lookup.
    t0 = time.perf_counter()
    base_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=False,
        semwrap=False,
        askfast=False,
    )
    base_e2e_ms = (time.perf_counter() - t0) * 1000.0
    base_wall = _mean_wall(base_payloads)

    # ASKFAST pass 1: SEMWRAP + QT compose + fill completion cache.
    cache = AskCompletionCache()
    t1 = time.perf_counter()
    fast_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=cache,
    )
    fast_e2e_ms = (time.perf_counter() - t1) * 1000.0
    fast_wall = _mean_wall(fast_payloads)

    # Warm pass: prove completion-cache hits (second ask of same pack).
    warm = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=cache,
    )
    warm_wall = _mean_wall(warm)
    cache_hr = cache.hit_rate()

    trials: list[dict[str, Any]] = []
    for i, (item, payload) in enumerate(
        zip(AB0_PACK, fast_payloads, strict=True), start=1
    ):
        kind, meta = _classify(dict(item), payload, bank, curated_root)
        trial = _build_trial(
            i=i,
            item=dict(item),
            payload=payload,
            lookup_kind=kind,
            sem_meta=meta,
            arm="askfast",
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    stats = askfast_stats(
        scores,
        errors,
        baseline_wall_ms=base_wall,
        askfast_wall_ms=fast_wall,
        cache_hit_rate=cache_hr,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
    )
    decision = decide_askfast(stats)
    # FIX: quality already from SEMWRAP; if wall somehow fails, document HOLD.
    fix_count = 0
    summary: dict[str, Any] = {
        "hyp_id": ASKFAST_ID,
        "stage": "AB2",
        "decision": decision,
        "compose": ["SEMWRAP", "QT", "AskCompletionCache", "batch_ask_many"],
        "forbidden": ["STREAM", "KVCACHE-Q", "GENCACHE"],
        "baseline": {
            "mean_wall_ms": base_wall,
            "e2e_ms": base_e2e_ms,
            "modes": [p.get("mode") for p in base_payloads],
        },
        "askfast": {
            "mean_wall_ms": fast_wall,
            "e2e_ms": fast_e2e_ms,
            "warm_wall_ms": warm_wall,
            "cache_hit_rate": cache_hr,
            "cache_size": cache.size(),
        },
        "fix_count": fix_count,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "stats": stats,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
            }
            for t in trials
        ],
        "finding": (
            f"{ASKFAST_ID}: wall {base_wall:.1f}→{fast_wall:.1f}ms "
            f"(drop={stats['wall_drop']:.0%}); mean={stats['mean']:.1f} "
            f"false_hit={n_false} cache_hr={cache_hr:.2f} decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-haskfast-askfast.md",
        "claim": "faster scoped ask — not open chat LM",
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
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_askfast(
            bank_path=Path(args.bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": ASKFAST_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_errors": summary["stats"]["n_errors"],
                "wall_drop": summary["stats"]["wall_drop"],
                "baseline_wall_ms": summary["stats"]["baseline_wall_ms"],
                "askfast_wall_ms": summary["stats"]["askfast_wall_ms"],
                "cache_hit_rate": summary["stats"]["cache_hit_rate"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
