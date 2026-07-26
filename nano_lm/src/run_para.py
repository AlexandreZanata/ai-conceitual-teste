"""Wave AA1 H-PARA runner: paraphrase HITL×10 on wrap (nano:para)."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from matrix_common import REPO, write_json
from para_ops import (
    PARA_ID,
    PARA_PACK,
    classify_lookup,
    decide_para,
    para_stats,
    paraphrase_collides_bank,
    score_para_trial,
)
from run_z_ask import ask_many
from tipd_pair import tune_cpu_threads
from z_trial import validate_trial
from z_wrap import load_bank_rows, lookup_gold

_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_TRIALS = REPO / "results/nano-lm/wave-aa/trials"
_SUMMARY = REPO / "results/nano-lm/wave-aa/para_summary.json"
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


def _build_trial(
    *,
    i: int,
    item: dict[str, str],
    payload: dict[str, Any],
    lookup_kind: str,
) -> dict[str, Any]:
    tid = f"AA1-{i:02d}"
    mode = str(payload.get("mode", ""))
    score, err, notes = score_para_trial(
        mode=mode,
        completion=str(payload.get("completion", "")),
        parent_gold=str(item["parent_gold"]),
        lookup_kind=lookup_kind,
    )
    trial: dict[str, Any] = {
        "trial_id": tid,
        "stage": "AA1",
        "hyp_id": PARA_ID,
        "question": item["paraphrase"],
        "parent_question": item["parent_question"],
        "source_id": item["source_id"],
        "recipe_id": payload.get("recipe_id"),
        "ckpt": None,
        "completion": payload.get("completion"),
        "wall_ms": payload.get("wall_ms"),
        "n_new": payload.get("n_new"),
        "seed": payload.get("seed", 0),
        "mode": mode,
        "lookup_kind": lookup_kind,
        "score": score,
        "error": err,
        "judge_model_name": _JUDGE,
        "judge_notes": notes,
        "manual_adjust": (
            "document wrap exact-match brittleness"
            if lookup_kind == "MISS"
            else (
                "investigate false-hit collision"
                if lookup_kind == "FALSE_HIT"
                else "no change — paraphrase true-hit"
            )
        ),
        "gold": str(item["parent_gold"]).strip(),
        "repaired": str(item["parent_gold"]).strip(),
        "wrap_id": payload.get("wrap_id"),
        "weight_update": False,
    }
    errs = validate_trial(trial)
    if errs:
        raise ValueError(f"{tid}: " + "; ".join(errs))
    return trial


def run_para(
    *,
    bank_path: Path,
    root: Path,
    out: Path,
    trials_dir: Path,
    seed: int = 0,
) -> dict[str, Any]:
    """
    GIVEN Z1 paraphrases + wrap bank
    WHEN ask_many(--wrap) ×10
    THEN score false-hit/miss; decision PROMOTE|HOLD|KILL.
    """
    bank = load_bank_rows(bank_path)
    collide = paraphrase_collides_bank(PARA_PACK, bank)
    if collide:
        raise ValueError(f"paraphrase collides bank keys: {collide[:2]}")

    questions = [p["paraphrase"] for p in PARA_PACK]
    kinds: list[str] = []
    for item in PARA_PACK:
        looked = lookup_gold(item["paraphrase"], bank)
        kinds.append(classify_lookup(looked, item["parent_gold"]))

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
    for i, (item, payload, kind) in enumerate(
        zip(PARA_PACK, payloads, kinds, strict=True), start=1
    ):
        # Reconcile: if ask returned WRAP_LOOKUP, re-classify vs parent gold.
        if str(payload.get("mode")) == "WRAP_LOOKUP":
            kind = classify_lookup(str(payload.get("completion")), item["parent_gold"])
        trial = _build_trial(
            i=i, item=dict(item), payload=payload, lookup_kind=kind
        )
        write_json(trials_dir / f"{trial['trial_id']}.json", trial)
        trials.append(trial)

    scores = [float(t["score"]) for t in trials]
    errors = [bool(t["error"]) for t in trials]
    n_true = sum(1 for t in trials if t["lookup_kind"] == "TRUE_HIT")
    n_false = sum(1 for t in trials if t["lookup_kind"] == "FALSE_HIT")
    n_miss = sum(1 for t in trials if t["lookup_kind"] == "MISS")
    stats = para_stats(
        scores, errors, n_true_hit=n_true, n_false_hit=n_false, n_miss=n_miss
    )
    decision = decide_para(stats)
    summary: dict[str, Any] = {
        "hyp_id": PARA_ID,
        "stage": "AA1",
        "decision": decision,
        "bank_path": str(bank_path),
        "bank_rows": len(bank),
        "weight_update": False,
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
            f"{PARA_ID}: paraphrase stress; mean={stats['mean']:.1f} "
            f"false_hit={n_false} miss={n_miss} true_hit={n_true} "
            f"decision={decision}."
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
    threads = tune_cpu_threads(max(4, int(os.cpu_count() or 4) - 2))
    try:
        summary = run_para(
            bank_path=Path(args.bank),
            root=Path(args.root),
            out=Path(args.out),
            trials_dir=Path(args.trials_dir),
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
                "hyp_id": PARA_ID,
                "decision": decision,
                "mean": summary["stats"]["mean"],
                "n_errors": summary["stats"]["n_errors"],
                "n_false_hit": summary["stats"]["n_false_hit"],
                "n_miss": summary["stats"]["n_miss"],
                "cpu_threads": threads,
                "out": str(args.out),
            }
        )
    )
    # HOLD documents brittleness (allowed gate); only KILL fails the runner.
    return 0 if decision in {"PROMOTE", "HOLD"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
