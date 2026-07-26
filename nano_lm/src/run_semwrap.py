"""Wave AB1 H-SEMWRAP runner: fuzzy wrap HITL×10 (nano:semwrap)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ab_session_ops import AB0_PACK
from matrix_common import REPO, write_json
from run_z_ask import ask_many
from semwrap_ops import (
    SEMWRAP_ID,
    SEMWRAP_N,
    alias_bank_row,
    classify_semwrap,
    decide_semwrap,
    score_semwrap_trial,
    semantic_lookup,
    semwrap_stats,
)
from tipd_pair import tune_cpu_threads
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-ab/trials"
_SUMMARY = REPO / "results/nano-lm/wave-ab/semwrap_summary.json"
_AB_BANK = REPO / "results/nano-lm/wave-ab/error_bank.jsonl"
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


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
    sem_meta: dict[str, Any],
    pass_idx: int,
) -> dict[str, Any]:
    tid = f"AB-SEMWRAP-HITL-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes = score_semwrap_trial(
        mode=mode,
        completion=str(payload.get("completion", "")),
        expected_gold=str(item["gold"]),
        lookup_kind=lookup_kind,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AB1",
        "hyp_id": SEMWRAP_ID,
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
            "no change — SEMWRAP true-hit"
            if lookup_kind == "TRUE_HIT"
            else (
                "FIX: threshold/margin or bank collision"
                if lookup_kind == "FALSE_HIT"
                else "FIX: alias gold for miss phrasing"
            )
        ),
        "gold": str(item["gold"]).strip(),
        "repaired": str(item["gold"]).strip(),
        "wrap_id": payload.get("wrap_id"),
        "weight_update": False,
        "pass_idx": pass_idx,
        "score_before": None,
        "score_after": score,
    }
    errs = validate_trial(trial)
    if errs:
        raise ValueError(f"{tid}: " + "; ".join(errs))
    return trial


def _classify_payload(
    item: dict[str, str],
    payload: dict[str, Any],
    bank: list[dict[str, Any]],
    curated_root: Path,
) -> tuple[str, dict[str, Any]]:
    mode = str(payload.get("mode", ""))
    if mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP"}:
        meta = dict(payload.get("semwrap") or {})
        gold, meta2 = semantic_lookup(
            item["question"], bank, curated_root=curated_root
        )
        meta = {**meta2, **meta}
        kind = classify_semwrap(
            str(payload.get("completion")),
            expected_gold=item["gold"],
            expected_source_id=item["source_id"],
            hit_source_id=str(meta.get("source_id") or "") or None,
        )
        # Prefer live completion classification; keep meta for audit.
        _ = gold
        return kind, meta
    gold, meta = semantic_lookup(
        item["question"], bank, curated_root=curated_root
    )
    kind = classify_semwrap(
        gold,
        expected_gold=item["gold"],
        expected_source_id=item["source_id"],
        hit_source_id=str(meta.get("source_id") or "") or None,
    )
    return kind, meta


def _ask_pack(
    *,
    bank_path: Path,
    root: Path,
    curated_root: Path,
    seed: int,
) -> list[dict[str, Any]]:
    questions = [p["question"] for p in AB0_PACK]
    return ask_many(
        questions=questions,
        root=root,
        seed=seed,
        semwrap=True,
        bank_path=bank_path,
        curated_root=curated_root,
    )


def _fix_misses(
    trials: list[dict[str, Any]],
    *,
    bank_path: Path,
    ab_bank: Path,
) -> list[dict[str, Any]]:
    """Append alias golds for MISS/error trials; return added rows."""
    added: list[dict[str, Any]] = []
    for t in trials:
        if not bool(t.get("error")):
            continue
        if str(t.get("lookup_kind")) == "FALSE_HIT":
            continue  # false-hit needs threshold FIX, not alias
        row = alias_bank_row(
            trial_id=str(t["trial_id"]),
            question=str(t["question"]),
            source_id=str(t["source_id"]),
            gold=str(t["gold"]),
        )
        append_error_row(bank_path, row)
        append_error_row(ab_bank, row)
        added.append(row)
        t["manual_adjust"] = "FIX applied: alias gold appended; re-ASK"
        t["score_before"] = float(t["score"])
    return added


def run_semwrap(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    curated_root: Path,
    ab_bank: Path,
    seed: int = 0,
    max_fix_passes: int = 1,
) -> dict[str, Any]:
    """
    GIVEN AB0 frozen asks + wrap bank
    WHEN ASK→EVAL→FIX×10 with SEMWRAP
    THEN decide PROMOTE|HOLD|KILL; log trials.
    """
    if len(AB0_PACK) != SEMWRAP_N:
        raise ValueError("AB0 pack must be 10")

    trials_dir.mkdir(parents=True, exist_ok=True)
    ab_bank.parent.mkdir(parents=True, exist_ok=True)
    if not ab_bank.is_file():
        ab_bank.write_text("", encoding="utf-8")

    fix_count = 0
    reask_improved = False
    pass_idx = 0
    trials: list[dict[str, Any]] = []
    while True:
        bank = load_bank_rows(bank_path)
        payloads = _ask_pack(
            bank_path=bank_path,
            root=root,
            curated_root=curated_root,
            seed=seed,
        )
        if len(payloads) != SEMWRAP_N:
            raise RuntimeError(f"expected 10 payloads, got {len(payloads)}")

        trials = []
        for i, (item, payload) in enumerate(
            zip(AB0_PACK, payloads, strict=True), start=1
        ):
            kind, meta = _classify_payload(
                dict(item), payload, bank, curated_root
            )
            trial = _build_trial(
                i=i,
                item=dict(item),
                payload=payload,
                lookup_kind=kind,
                sem_meta=meta,
                pass_idx=pass_idx,
            )
            write_json(trials_dir / f"{trial['trial_id']}.json", trial)
            trials.append(trial)

        scores = [float(t["score"]) for t in trials]
        errors = [bool(t["error"]) for t in trials]
        n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
        n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
        n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
        stats = semwrap_stats(
            scores,
            errors,
            n_true_hit=n_true,
            n_false_hit=n_false,
            n_miss=n_miss,
        )
        decision = decide_semwrap(stats)
        if decision == "PROMOTE" or n_false > 0:
            break
        if pass_idx >= max_fix_passes:
            break
        added = _fix_misses(
            trials, bank_path=bank_path, ab_bank=ab_bank
        )
        if not added:
            break
        fix_count += len(added)
        pass_idx += 1
        # Re-ASK after FIX.
        bank = load_bank_rows(bank_path)
        payloads2 = _ask_pack(
            bank_path=bank_path,
            root=root,
            curated_root=curated_root,
            seed=seed,
        )
        improved = 0
        for t, item, payload in zip(trials, AB0_PACK, payloads2, strict=True):
            if not bool(t.get("error")):
                continue
            kind, meta = _classify_payload(
                dict(item), payload, bank, curated_root
            )
            score, err, notes = score_semwrap_trial(
                mode=str(payload.get("mode", "")),
                completion=str(payload.get("completion", "")),
                expected_gold=str(item["gold"]),
                lookup_kind=kind,
            )
            before = float(t.get("score_before") or t["score"])
            t["score_after"] = score
            t["score"] = score
            t["error"] = err
            t["lookup_kind"] = kind
            t["mode"] = payload.get("mode")
            t["completion"] = payload.get("completion")
            t["semwrap"] = meta
            t["judge_notes"] = notes
            t["pass_idx"] = pass_idx
            write_json(trials_dir / f"{t['trial_id']}.json", t)
            if score > before:
                improved += 1
        reask_improved = improved > 0
        scores = [float(t["score"]) for t in trials]
        errors = [bool(t["error"]) for t in trials]
        n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
        n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
        n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
        stats = semwrap_stats(
            scores,
            errors,
            n_true_hit=n_true,
            n_false_hit=n_false,
            n_miss=n_miss,
        )
        decision = decide_semwrap(stats)
        break

    summary: dict[str, Any] = {
        "hyp_id": SEMWRAP_ID,
        "stage": "AB1",
        "decision": decision,
        "bank_path": str(bank_path),
        "bank_rows": len(load_bank_rows(bank_path)),
        "weight_update": False,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "fix_count": fix_count,
        "reask_improved": reask_improved,
        "stats": stats,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "app_id": t["app_id"],
                "mode": t["mode"],
                "lookup_kind": t["lookup_kind"],
                "score": t["score"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
                "score_before": t.get("score_before"),
                "score_after": t.get("score_after"),
            }
            for t in trials
        ],
        "finding": (
            f"{SEMWRAP_ID}: fuzzy wrap; mean={stats['mean']:.1f} "
            f"false_hit={stats['n_false_hit']} miss={stats['n_miss']} "
            f"true_hit={stats['n_true_hit']} fix={fix_count} "
            f"decision={decision}."
        ),
        "public_note": "docs/results/nano-lm/formal-hsemwrap-semwrap.md",
        "claim": "scoped near-known ask — not open chat LM",
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
    ap.add_argument("--ab-bank", type=Path, default=_AB_BANK)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--max-fix-passes", type=int, default=1)
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))
    # Warm curated existence checks in parallel (IO), leave cores for torch later.
    from curated_sources import SOURCES

    paths = [
        Path(args.curated) / str(s["path"])
        for s in SOURCES
        if str(s["id"]) in {p["source_id"] for p in AB0_PACK}
    ]
    with ThreadPoolExecutor(max_workers=min(12, max(4, cpus - 4))) as pool:
        list(pool.map(lambda p: p.is_file(), paths))
    try:
        summary = run_semwrap(
            bank_path=Path(args.bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            curated_root=Path(args.curated),
            ab_bank=Path(args.ab_bank),
            seed=int(args.seed),
            max_fix_passes=int(args.max_fix_passes),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    decision = str(summary["decision"])
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": SEMWRAP_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_errors": summary["stats"]["n_errors"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "n_miss": summary["stats"]["n_miss"],
                "n_true_hit": summary["stats"]["n_true_hit"],
                "fix_count": summary["fix_count"],
                "reask_improved": summary["reask_improved"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
