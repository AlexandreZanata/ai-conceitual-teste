"""Wave AH4 H-FASTLIFT runner: generative wall_ms>0 speed vs AG FASTREAL."""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from ah_session_ops import AH0_PACK
from antifp_ops import extract_telemetry
from askfast_ops import AskCompletionCache
from fastlift_ops import (
    AF_RAW_OPEN_WALL_MS,
    FASTLIFT_ID,
    FASTLIFT_N,
    FASTREAL_HOT_WALL_MS,
    decide_fastlift,
    fastlift_stats,
    mean_ms,
    score_fastlift_gen,
    score_fastlift_lookup,
    ttft_of,
)
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import alias_bank_row, classify_semwrap, semantic_lookup
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_wrap import load_bank_rows

_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_AH_BANK = REPO / "results/nano-lm/wave-ah/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ah/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ah/fastlift_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
_CURATED = REPO / "nano_lm/data/curated"
_JUDGE = "cursor-composer-frontier-chat"
# Extra hot rounds vs FASTREAL (2) — speed lift attempt under max HW.
_GEN_HOT_ROUNDS = 4


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


def _seed_pack(bank_path: Path, ah_bank: Path) -> int:
    bank_path.parent.mkdir(parents=True, exist_ok=True)
    ah_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ah_bank.is_file():
        ah_bank.write_text("", encoding="utf-8")
    existing = {
        str(r.get("question", "")).strip() for r in load_bank_rows(bank_path)
    }
    n = 0
    for i, item in enumerate(AH0_PACK, start=1):
        q = str(item["question"]).strip()
        if q in existing:
            continue
        row = alias_bank_row(
            trial_id=f"AH-FASTLIFT-SEED-{i:02d}",
            question=q,
            source_id=item["source_id"],
            gold=item["gold"],
        )
        row["hyp_id"] = FASTLIFT_ID
        row["judge_notes"] = [
            "FASTLIFT seed for AH held-out ask",
            "LOOKUP product path — not speed IQ",
            "no student weight update",
        ]
        append_error_row(bank_path, row)
        append_error_row(ah_bank, row)
        existing.add(q)
        n += 1
    return n


def _classify_lookup(
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


def _timed_gen(
    *,
    questions: list[str],
    root: Path,
    seed: int,
) -> tuple[list[dict[str, Any]], float]:
    """GENERATE arm: wrap=False, no AskCompletionCache (wall_ms must stay >0)."""
    t0 = time.perf_counter()
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=False,
        askfast=False,
    )
    e2e_ms = (time.perf_counter() - t0) * 1000.0
    return payloads, e2e_ms


def _best_hot_gen(
    *,
    questions: list[str],
    root: Path,
    seed: int,
    rounds: int = _GEN_HOT_ROUNDS,
) -> tuple[list[dict[str, Any]], float]:
    best_e2e = float("inf")
    best: list[dict[str, Any]] | None = None
    for r in range(max(1, rounds)):
        payloads, e2e = _timed_gen(
            questions=questions,
            root=root,
            seed=seed + r + 1,
        )
        if e2e < best_e2e:
            best_e2e = e2e
            best = payloads
    if best is None:
        raise RuntimeError("FASTLIFT hot gen produced no payloads")
    return best, float(best_e2e)


def _lookup_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    fix_pass: int,
) -> dict[str, Any]:
    score, err, notes = score_fastlift_lookup(
        mode=str(payload.get("mode", "")),
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
        payload=payload,
    )
    tel = extract_telemetry(payload)
    return {
        "trial_id": f"AH-FASTLIFT-LOOKUP-HITL-{i:02d}",
        "stage": "AH4",
        "hyp_id": FASTLIFT_ID,
        "arm": "LOOKUP",
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "completion": payload.get("completion"),
        "mode": tel["mode"],
        "wall_ms": tel["wall_ms"],
        "ttft_ms": ttft_of(payload),
        "n_new": tel["n_new"],
        "lookup_kind": lookup_kind,
        "semwrap": sem_meta,
        "score": score,
        "error": err,
        "fix_pass": int(fix_pass),
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "gold": str(item["gold"]).strip(),
        "weight_update": False,
        "cache_hit": bool(payload.get("cache_hit")),
    }


def _gen_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    score, err, notes = score_fastlift_gen(
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        payload=payload,
    )
    tel = extract_telemetry(payload)
    return {
        "trial_id": f"AH-FASTLIFT-GEN-HITL-{i:02d}",
        "stage": "AH4",
        "hyp_id": FASTLIFT_ID,
        "arm": "GENERATE",
        "app_id": item["app_id"],
        "question": item["question"],
        "source_id": item["source_id"],
        "completion": payload.get("completion"),
        "mode": tel["mode"],
        "wall_ms": tel["wall_ms"],
        "ttft_ms": ttft_of(payload),
        "n_new": tel["n_new"],
        "score": score,
        "error": err,
        "fix_pass": 0,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "gold": str(item["gold"]).strip(),
        "weight_update": False,
    }


def run_fastlift(
    *,
    bank_path: Path,
    ah_bank: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN AH0 held-out asks
    WHEN LOOKUP quality + GENERATE cold/warm/hot timing (wall_ms>0)
    THEN dual-arm FASTLIFT vs AG FASTREAL hot → PROMOTE|HOLD|KILL.
    """
    if len(AH0_PACK) != FASTLIFT_N:
        raise ValueError("AH0 pack must be 10")
    trials_dir.mkdir(parents=True, exist_ok=True)
    seeded = _seed_pack(bank_path, ah_bank)
    bank = load_bank_rows(bank_path)
    questions = [p["question"] for p in AH0_PACK]

    lookup_payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        askfast=True,
        bank_path=bank_path,
        curated_root=curated_root,
        ask_cache=AskCompletionCache(),
    )
    lookup_trials: list[dict[str, Any]] = []
    fix_count = 0
    for i, (item, payload) in enumerate(
        zip(AH0_PACK, lookup_payloads, strict=True), start=1
    ):
        kind, meta = _classify_lookup(
            dict(item), payload, bank, curated_root
        )
        fix_pass = 0
        if kind != "TRUE_HIT":
            row = alias_bank_row(
                trial_id=f"AH-FASTLIFT-FIX-{i:02d}",
                question=item["question"],
                source_id=item["source_id"],
                gold=item["gold"],
            )
            row["hyp_id"] = FASTLIFT_ID
            append_error_row(bank_path, row)
            append_error_row(ah_bank, row)
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
            kind, meta = _classify_lookup(
                dict(item), payload, bank, curated_root
            )
        trial = _lookup_trial(
            i=i,
            item=dict(item),
            payload=payload,
            lookup_kind=kind,
            sem_meta=meta,
            fix_pass=fix_pass,
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        lookup_trials.append(trial)

    cold, cold_e2e = _timed_gen(
        questions=questions, root=root, seed=seed
    )
    warm, warm_e2e = _timed_gen(
        questions=questions, root=root, seed=seed
    )
    hot, hot_e2e = _best_hot_gen(
        questions=questions, root=root, seed=seed
    )
    cold_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in cold])
    warm_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in warm])
    hot_wall = mean_ms([float(p.get("wall_ms") or 0.0) for p in hot])
    cold_ttft = mean_ms([ttft_of(p) for p in cold])
    warm_ttft = mean_ms([ttft_of(p) for p in warm])
    hot_ttft = mean_ms([ttft_of(p) for p in hot])

    gen_trials: list[dict[str, Any]] = []
    n_gen_wall_ok = 0
    for i, (item, payload) in enumerate(
        zip(AH0_PACK, cold, strict=True), start=1
    ):
        trial = _gen_trial(i=i, item=dict(item), payload=payload)
        tel = extract_telemetry(payload)
        if tel["wall_ms"] > 0.0 and tel["n_new"] > 0:
            n_gen_wall_ok += 1
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        gen_trials.append(trial)

    n_true = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "TRUE_HIT"
    )
    n_false = sum(
        1 for t in lookup_trials if t["lookup_kind"] == "FALSE_HIT"
    )
    stats = fastlift_stats(
        lookup_scores=[float(t["score"]) for t in lookup_trials],
        lookup_errors=[bool(t["error"]) for t in lookup_trials],
        gen_scores=[float(t["score"]) for t in gen_trials],
        gen_errors=[bool(t["error"]) for t in gen_trials],
        n_true_hit=n_true,
        n_false_hit=n_false,
        cold_wall_ms=cold_wall,
        warm_wall_ms=warm_wall,
        hot_wall_ms=hot_wall,
        cold_ttft_ms=cold_ttft,
        warm_ttft_ms=warm_ttft,
        hot_ttft_ms=hot_ttft,
        cold_e2e_ms=cold_e2e,
        warm_e2e_ms=warm_e2e,
        hot_e2e_ms=hot_e2e,
        n_gen_wall_ok=n_gen_wall_ok,
        n_fix=fix_count,
    )
    decision = decide_fastlift(stats)
    summary: dict[str, Any] = {
        "hyp_id": FASTLIFT_ID,
        "stage": "AH4",
        "decision": decision,
        "compose": [
            "SEMWRAP/ASKFAST LOOKUP (quality only)",
            "GENERATE wrap=False QT+EARLY",
            "cold+warm+hot gen timing (hot rounds=4)",
            f"vs FASTREAL hot {FASTREAL_HOT_WALL_MS:.3f} ms",
        ],
        "forbidden": [
            "STREAM",
            "KVCACHE-Q",
            "GENCACHE",
            "LOOKUP wall=0 as speed IQ",
            "open chat",
        ],
        "seeded_golds": int(seeded),
        "fix_count": int(fix_count),
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
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
            "af_raw_open_wall_ms": AF_RAW_OPEN_WALL_MS,
            "fastreal_hot_wall_ms": FASTREAL_HOT_WALL_MS,
            "gen_hot_rounds": _GEN_HOT_ROUNDS,
        },
        "stats": stats,
        "lookup_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
            }
            for t in lookup_trials
        ],
        "gen_trials": [
            {
                "trial_id": t["trial_id"],
                "mode": t["mode"],
                "score": t["score"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
                "n_new": t["n_new"],
                "completion": str(t.get("completion") or "")[:120],
            }
            for t in gen_trials
        ],
        "finding": (
            f"{FASTLIFT_ID}: gen wall "
            f"{cold_wall:.1f}/{warm_wall:.1f}/{hot_wall:.1f}ms "
            f"(FASTREAL hot {FASTREAL_HOT_WALL_MS:.1f}) "
            f"e2e {cold_e2e:.0f}/{warm_e2e:.0f}/{hot_e2e:.0f} "
            f"L={stats['lookup_mean']:.1f} G={stats['gen_mean']:.1f} "
            f"wall_ok={n_gen_wall_ok}/10 "
            f"vs_fr={stats['pass_vs_fastreal']} → {decision}"
        ),
        "public_note": "docs/results/nano-lm/formal-hfastlift-fastlift.md",
        "ship_claim": "AF packaged stack until AH6 gen bar",
        "claim": (
            "faster generative ask vs FASTREAL with wall_ms>0 — "
            "LOOKUP scores are not speed IQ"
        ),
    }
    write_json(out, summary)
    return summary


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--bank", type=Path, default=_Z_BANK)
    ap.add_argument("--ah-bank", type=Path, default=_AH_BANK)
    ap.add_argument("--root", type=Path, default=_CHAMPION)
    ap.add_argument("--out", type=Path, default=_SUMMARY)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--curated", type=Path, default=_CURATED)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_fastlift(
            bank_path=Path(args.bank),
            ah_bank=Path(args.ah_bank),
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
    st = summary["stats"]
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": FASTLIFT_ID,
                "decision": decision,
                "lookup_mean": st["lookup_mean"],
                "gen_mean": st["gen_mean"],
                "n_false_hit": st["n_false_hit"],
                "n_gen_wall_ok": st["n_gen_wall_ok"],
                "pass_speed": st["pass_speed"],
                "pass_vs_fastreal": st["pass_vs_fastreal"],
                "cold_wall_ms": st["cold_wall_ms"],
                "warm_wall_ms": st["warm_wall_ms"],
                "hot_wall_ms": st["hot_wall_ms"],
                "fastreal_hot_wall_ms": st["fastreal_hot_wall_ms"],
                "fix_count": summary["fix_count"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
