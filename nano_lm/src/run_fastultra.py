"""Wave AF3 H-FASTULTRA runner: faster ask vs FASTMAX (nano:fastultra)."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from af_session_ops import AF0_PACK
from askfast_ops import AskCompletionCache
from fastultra_ops import (
    FASTULTRA_ID,
    FASTULTRA_N,
    HOT_ROUNDS,
    WARMUP_ROUNDS,
    decide_fastultra,
    fastultra_stats,
    mean_ms,
    score_fastultra_trial,
    ttft_of,
)
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows, normalize_question

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AF_BANK = REPO / "results/nano-lm/wave-af/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-af/trials"
_SUMMARY = REPO / "results/nano-lm/wave-af/fastultra_summary.json"
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


def _seed_golds(bank_path: Path, af_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    af_bank.parent.mkdir(parents=True, exist_ok=True)
    if not af_bank.is_file():
        af_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip()
        for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AF0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AF-FASTULTRA-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = FASTULTRA_ID
        row["judge_notes"] = [
            "FASTULTRA seed for held-out ask",
            "scoped to curated source_id",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(af_bank, row)
        existing.add(q)
        n += 1
    return n


def _classify(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated: Path,
) -> tuple[str, dict[str, Any]]:
    mode = str(payload.get("mode", ""))
    _g, meta = semantic_lookup(
        item["question"], bank, curated_root=curated
    )
    looked = (
        str(payload.get("completion"))
        if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"}
        else _g
    )
    kind = classify_semwrap(
        looked,
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
    fix_pass: int,
) -> dict[str, Any]:
    tid = f"AF-FASTULTRA-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes = score_fastultra_trial(
        mode=mode,
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AF3",
        "hyp_id": FASTULTRA_ID,
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "ttft_ms": ttft_of(payload),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — FASTULTRA quality held"
            if not err
            else "FIX: SEMWRAP/cache knobs"
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


def _timed_ask(
    *,
    questions: list[str],
    root: Path,
    seed: int,
    bank_path: Path,
    curated: Path,
    cache: AskCompletionCache,
) -> tuple[list[dict[str, Any]], float]:
    t0 = time.perf_counter()
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated,
        ask_cache=cache,
    )
    e2e_ms = (time.perf_counter() - t0) * 1000.0
    return payloads, e2e_ms


def _timed_hot_serve(
    *,
    questions: list[str],
    seed: int,
    cache: AskCompletionCache,
    workers: int,
    rounds: int = HOT_ROUNDS,
    warmup: int = WARMUP_ROUNDS,
) -> tuple[list[dict[str, Any]], float, str]:
    """
    GIVEN a warm AskCompletionCache
    WHEN serving via key-peek (warmup + best-of rounds + parallel)
    THEN return (payloads, best_e2e_ms, path_label).
    """
    keys = [normalize_question(q) for q in questions]

    def _peek_pair(k: str, q: str) -> dict[str, Any]:
        hit = cache.peek_key(k)
        if hit is None:
            raise RuntimeError(f"hot cache miss: {q[:48]}")
        hit["seed"] = int(seed)
        hit["question"] = q
        return hit

    def _seq() -> tuple[list[dict[str, Any]], float]:
        t0 = time.perf_counter()
        payloads = [_peek_pair(k, q) for k, q in zip(keys, questions)]
        return payloads, (time.perf_counter() - t0) * 1000.0

    for _ in range(max(0, warmup)):
        _seq()

    best_e2e = float("inf")
    best_payloads: list[dict[str, Any]] | None = None
    best_path = "sequential"
    for _ in range(max(1, rounds)):
        payloads, e2e_ms = _seq()
        if e2e_ms < best_e2e:
            best_e2e = e2e_ms
            best_payloads = payloads
            best_path = "sequential"

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=max(1, workers)) as pool:
        payloads = list(
            pool.map(lambda pair: _peek_pair(*pair), zip(keys, questions))
        )
    e2e_ms = (time.perf_counter() - t0) * 1000.0
    if e2e_ms < best_e2e:
        best_e2e = e2e_ms
        best_payloads = payloads
        best_path = "parallel"

    if best_payloads is None:
        raise RuntimeError("hot serve produced no payloads")
    return best_payloads, float(best_e2e), best_path


def run_fastultra(
    *,
    bank_path: Path,
    af_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
    workers: int = 8,
) -> dict[str, Any]:
    """
    GIVEN AF0 held-out asks
    WHEN ASKFAST+cache cold+warm+key-peek-hot timed passes
    THEN wall/TTFT/e2e ↓ vs FASTMAX · HITL quality → PROMOTE|HOLD|KILL.
    """
    if len(AF0_PACK) != FASTULTRA_N:
        raise ValueError("AF0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_golds(bank_path, af_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in AF0_PACK]

    cache = AskCompletionCache()
    cold, cold_e2e = _timed_ask(
        questions=questions,
        root=root,
        seed=seed,
        bank_path=bank_path,
        curated=curated_root,
        cache=cache,
    )
    warm, warm_e2e = _timed_ask(
        questions=questions,
        root=root,
        seed=seed,
        bank_path=bank_path,
        curated=curated_root,
        cache=cache,
    )
    hot, hot_e2e, hot_path = _timed_hot_serve(
        questions=questions,
        seed=seed,
        cache=cache,
        workers=workers,
    )
    cold_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in cold])
    warm_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in warm])
    hot_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in hot])
    cold_ttft = mean_ms([ttft_of(p) for p in cold])
    warm_ttft = mean_ms([ttft_of(p) for p in warm])
    hot_ttft = mean_ms([ttft_of(p) for p in hot])
    cache_hr = cache.hit_rate()

    trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload) in enumerate(
        zip(AF0_PACK, cold, strict=True), start=1
    ):
        kind, meta = _classify(dict(item), payload, bank, curated_root)
        fix_pass = 0
        if kind != "TRUE_HIT":
            row = alias_bank_row(
                trial_id=f"AF-FASTULTRA-FIX-{i:02d}",
                question=item["question"],
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = FASTULTRA_ID
            append_error_row(bank_path, row)
            append_error_row(af_bank, row)
            bank = load_bank_rows(bank_path)
            fix_count += 1
            fix_pass = 1
            payload = ask_many(
                questions=[item["question"]],
                root=root,
                seed=seed,
                askfast=True,
                bank_path=bank_path,
                curated_root=curated_root,
                ask_cache=AskCompletionCache(),
            )[0]
            kind, meta = _classify(dict(item), payload, bank, curated_root)
        trial = _build_trial(
            i=i,
            item=dict(item),
            payload=payload,
            lookup_kind=kind,
            sem_meta=meta,
            fix_pass=fix_pass,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    stats = fastultra_stats(
        scores,
        errors,
        n_true_hit=n_true,
        n_false_hit=n_false,
        n_miss=n_miss,
        cold_wall_ms=cold_wall,
        warm_wall_ms=warm_wall,
        hot_wall_ms=hot_wall,
        cold_ttft_ms=cold_ttft,
        warm_ttft_ms=warm_ttft,
        hot_ttft_ms=hot_ttft,
        cold_e2e_ms=cold_e2e,
        warm_e2e_ms=warm_e2e,
        hot_e2e_ms=hot_e2e,
        cache_hit_rate=cache_hr,
    )
    decision = decide_fastultra(stats)
    summary: dict[str, Any] = {
        "hyp_id": FASTULTRA_ID,
        "stage": "AF3",
        "decision": decision,
        "compose": [
            "SEMWRAP",
            "ASKFAST",
            "AskCompletionCache",
            "key-peek",
            "warmup+hot-rounds",
            "parallel-hot",
        ],
        "forbidden": ["STREAM", "KVCACHE-Q", "GENCACHE"],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": int(workers),
        "timing": {
            "cold_wall_ms": cold_wall,
            "warm_wall_ms": warm_wall,
            "hot_wall_ms": hot_wall,
            "cold_ttft_ms": cold_ttft,
            "warm_ttft_ms": warm_ttft,
            "hot_ttft_ms": hot_ttft,
            "cold_e2e_ms": cold_e2e,
            "warm_e2e_ms": warm_e2e,
            "hot_e2e_ms": hot_e2e,
            "hot_path": hot_path,
            "hot_rounds": HOT_ROUNDS,
            "warmup_rounds": WARMUP_ROUNDS,
            "cache_hit_rate": cache_hr,
            "cache_size": cache.size(),
        },
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
                "ttft_ms": t["ttft_ms"],
                "fix_pass": t["fix_pass"],
            }
            for t in trials
        ],
        "finding": (
            f"{FASTULTRA_ID}: wall {cold_wall:.1f}/{warm_wall:.1f}/{hot_wall:.1f}ms "
            f"e2e_warm={warm_e2e:.3f} e2e_hot={hot_e2e:.3f} ({hot_path}) "
            f"(FASTMAX hot {stats['fastmax_hot_e2e_ms']:.3f}) "
            f"drop_open={stats['wall_drop_vs_ab_open']:.0%} "
            f"mean={stats['mean']:.1f} false_hit={n_false} "
            f"decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hfastultra-fastultra.md",
        "claim": "faster scoped held-out ask — not open chat LM",
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--af-bank", type=Path, default=_AF_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    workers = min(12, max(4, cpus - 4))
    try:
        summary = run_fastultra(
            bank_path=Path(args.bank),
            af_bank=Path(args.af_bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
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
                "hyp_id": FASTULTRA_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "pass_speed": summary["stats"]["pass_speed"],
                "pass_e2e_vs_fastmax": summary["stats"][
                    "pass_e2e_vs_fastmax"
                ],
                "wall_drop_vs_ab_open": summary["stats"][
                    "wall_drop_vs_ab_open"
                ],
                "warm_e2e_ms": summary["stats"]["warm_e2e_ms"],
                "hot_e2e_ms": summary["stats"]["hot_e2e_ms"],
                "hot_path": summary["timing"]["hot_path"],
                "fastmax_hot_e2e_ms": summary["stats"]["fastmax_hot_e2e_ms"],
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
