"""Wave AA0 H-WRAPBANK runner: expand error_bank golds + HITL×10 wrap (nano:wrapbank)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from matrix_common import REPO, write_json
from run_z_ask import ask_many
from tipd_pair import tune_cpu_threads
from wrapbank_ops import (
    WRAPBANK_ID,
    WRAPBANK_PACK,
    decide_wrapbank,
    expand_bank_rows,
    score_wrap_hit,
    wrapbank_stats,
)
from z_error_bank import append_error_row
from z_trial import validate_trial
from z_wrap import load_bank_rows

_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-aa/trials"
_SUMMARY = REPO / "results/nano-lm/wave-aa/wrapbank_summary.json"
_CHAMPION = REPO / "results/nano-lm/wave-z/models/champion"
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


def _append_added(path: Path, added: list[dict[str, Any]]) -> None:
    for row in added:
        append_error_row(path, row)


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
) -> dict[str, Any]:
    tid = f"AA0-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes = score_wrap_hit(
        str(payload.get("completion", "")),
        str(item["gold"]),
    )
    if mode != "WRAP_LOOKUP":
        score, err = 1.0, True
        notes = [
            "expected WRAP_LOOKUP after bank expansion",
            "decode path is not the WRAPBANK product claim",
            "mark error for bank/HITL audit",
        ]
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AA0",
        "hyp_id": WRAPBANK_ID,
        "question": item["question"],
        "source_id": item["source_id"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "no change — WRAPBANK lookup held"
            if mode == "WRAP_LOOKUP" and not err
            else "investigate bank miss"
        ),
        "gold": str(item["gold"]).strip(),
        "repaired": str(item["gold"]).strip(),
        "wrap_id": payload.get("wrap_id"),
        "weight_update": False,
    }
    errs = validate_trial(trial)
    if errs:
        raise ValueError(f"{tid}: " + "; ".join(errs))
    return trial


def run_wrapbank(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN WRAPBANK pack + champion wrap
    WHEN expand bank then ask_many(--wrap) ×10
    THEN write trials + summary; decision PROMOTE|KILL; no weight update.
    """
    existing = load_bank_rows(bank_path)
    added, _merged = expand_bank_rows(existing, WRAPBANK_PACK)
    if added:
        _append_added(bank_path, added)

    questions = [p["question"] for p in WRAPBANK_PACK]
    payloads = ask_many(
        questions=questions,
        root=root,
        seed=seed,
        wrap=True,
        bank_path=bank_path,
    )
    if len(payloads) != 10:
        raise RuntimeError(f"expected 10 payloads, got {len(payloads)}")

    trials_dir.mkdir(parents=True, exist_ok=True)
    trials: list[dict[str, Any]] = []
    for i, (item, payload) in enumerate(zip(WRAPBANK_PACK, payloads, strict=True), start=1):
        trial = _build_trial(i=i, item=dict(item), payload=payload)
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_lookup = sum(1 for t in trials if t.get("mode") == "WRAP_LOOKUP")
    stats = wrapbank_stats(scores, errors, n_lookup=n_lookup)
    decision = decide_wrapbank(stats)
    bank_after = load_bank_rows(bank_path)
    summary: dict[str, Any] = {
        "hyp_id": WRAPBANK_ID,
        "stage": "AA0",
        "decision": decision,
        "bank_path": str(bank_path),
        "bank_rows_before": len(existing),
        "bank_rows_added": len(added),
        "bank_rows_after": len(bank_after),
        "weight_update": False,
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "stats": stats,
        "trials": [
            {
                "trial_id": t["trial_id"],
                "source_id": t["source_id"],
                "mode": t["mode"],
                "score": t["score"],
                "error": t["error"],
                "wall_ms": t["wall_ms"],
            }
            for t in trials
        ],
        "finding": (
            f"{WRAPBANK_ID}: expand wrap golds + HITL×10; "
            f"mean={stats['mean']:.1f} errors={stats['n_errors']}/10 "
            f"lookup={n_lookup}/10 decision={decision}."
        ),
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
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    # Max hardware without starving the desktop: leave 2 cores free.
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        summary = run_wrapbank(
            bank_path=Path(args.bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
            seed=int(args.seed),
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    print(
        json.dumps(
            {
                "ok": True,
                "hyp_id": WRAPBANK_ID,
                "decision": summary["decision"],
                "mean": summary["stats"]["mean"],
                "n_errors": summary["stats"]["n_errors"],
                "bank_rows_added": summary["bank_rows_added"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    return 0 if summary["decision"] == "PROMOTE" else 1


if __name__ == "__main__":
    raise SystemExit(main())
