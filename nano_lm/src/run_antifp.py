"""Wave AG1 H-ANTIFP runner (nano:antifp) — dual-arm anti-FP smoke."""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

from ag_session_ops import AG0_PACK
from antifp_ops import (
    ANTIFP_ID,
    ANTIFP_THESIS,
    antifp_stats,
    classify_arm,
    decide_antifp,
    extract_telemetry,
    gen_arm_ok,
    intelligence_promote_allowed,
    lookup_arm_ok,
    score_antifp_completion,
)
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ag/antifp_summary.json"
_TRIALS = REPO / "results/nano-lm/wave-ag/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-ag/error_bank.jsonl"

_KNOWN_Q = (
    "Write a short Python function named add that returns "
    "the sum of two integers a and b."
)
_KNOWN_GOLD = "def add(a, b):\n    return a + b"


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


def _append_error(row: dict[str, Any]) -> None:
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    with _ERROR_BANK.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")


def _trial_row(
    *,
    trial_id: str,
    arm: str,
    question: str,
    gold: str,
    payload: dict[str, Any],
) -> dict[str, Any]:
    tel = extract_telemetry(payload)
    scored_arm = classify_arm(payload)
    score, err, notes = score_antifp_completion(
        arm=scored_arm,
        completion=str(payload.get("completion", "")),
        gold=gold,
    )
    return {
        "trial_id": trial_id,
        "stage": "AG1",
        "hyp_id": ANTIFP_ID,
        "arm": arm,
        "classified_arm": scored_arm,
        "question": question,
        "gold": gold,
        "completion": payload.get("completion"),
        "mode": tel["mode"],
        "wall_ms": tel["wall_ms"],
        "n_new": tel["n_new"],
        "score": score,
        "error": err,
        "notes": notes,
        "status": "scored",
    }


def _write_trial(trials_dir: Path, row: dict[str, Any]) -> str:
    trials_dir.mkdir(parents=True, exist_ok=True)
    path = trials_dir / f"{row['trial_id']}.json"
    write_json(path, row)
    return str(path.relative_to(REPO))


def _run_lookup_smoke() -> dict[str, Any]:
    from run_z_ask import ask_once

    return ask_once(question=_KNOWN_Q, wrap=True, seed=0)


def _run_gen_smokes(questions: list[str]) -> list[dict[str, Any]]:
    from run_z_ask import ask_many

    return ask_many(questions=questions, wrap=False, seed=0)


def _smoke_pack_questions() -> list[tuple[str, str, str]]:
    """(trial_suffix, question, gold) — known + first 3 AG held-out."""
    rows: list[tuple[str, str, str]] = [
        ("KNOWN", _KNOWN_Q, _KNOWN_GOLD),
    ]
    for item in AG0_PACK[:3]:
        rows.append(
            (str(item["id"]), str(item["question"]), str(item["gold"]))
        )
    return rows


def _iq_gate_selfcheck() -> tuple[bool, bool]:
    rejects = not intelligence_promote_allowed(
        lookup_logged=True,
        gen_logged=False,
        claim="smarter generative IQ from LOOKUP-only HITL",
    )
    allows = intelligence_promote_allowed(
        lookup_logged=True,
        gen_logged=True,
        claim="smarter model with dual-arm generative evidence",
    )
    return rejects, allows


def _build_summary(
    *,
    decision: str,
    threads: int,
    lookup_row: dict[str, Any],
    gen_rows: list[dict[str, Any]],
    written: list[str],
    stats: dict[str, Any],
) -> dict[str, Any]:
    return {
        "id": ANTIFP_ID,
        "thesis": ANTIFP_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "stats": stats,
        "lookup_smoke": {
            "mode": lookup_row.get("mode"),
            "wall_ms": lookup_row.get("wall_ms"),
            "n_new": lookup_row.get("n_new"),
            "score": lookup_row.get("score"),
            "classified_arm": lookup_row.get("classified_arm"),
        },
        "gen_smoke": [
            {
                "trial_id": r["trial_id"],
                "mode": r.get("mode"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
                "score": r.get("score"),
                "classified_arm": r.get("classified_arm"),
            }
            for r in gen_rows
        ],
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "public_note": "docs/results/nano-lm/formal-hantifp-antifp.md",
        "rule": "pesquisa §5 AG1 · anti-FP dual-arm law",
        "next": "AG2 H-CTXREAL (ASK→EVAL→FIX×10 dual)",
        "claim": (
            "scoped AF packaged stack + anti-FP harness — "
            "not open chat LM"
        ),
    }


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 4))

    if args.skip_ask:
        print(json.dumps({"ok": False, "error": "AG1 requires ASK smoke"}))
        return 2

    try:
        lookup_payload = _run_lookup_smoke()
        pack = _smoke_pack_questions()
        gen_payloads = _run_gen_smokes([q for _, q, _ in pack])
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2

    trials_dir = Path(args.trials_dir)
    lookup_row = _trial_row(
        trial_id="AG-ANTIFP-LOOKUP-KNOWN",
        arm="LOOKUP",
        question=_KNOWN_Q,
        gold=_KNOWN_GOLD,
        payload=lookup_payload,
    )
    written = [_write_trial(trials_dir, lookup_row)]

    gen_rows: list[dict[str, Any]] = []
    for (suffix, question, gold), payload in zip(
        pack, gen_payloads, strict=True
    ):
        row = _trial_row(
            trial_id=f"AG-ANTIFP-GEN-{suffix}",
            arm="GENERATE",
            question=question,
            gold=gold,
            payload=payload,
        )
        written.append(_write_trial(trials_dir, row))
        gen_rows.append(row)
        if row["error"]:
            _append_error(
                {
                    "hyp_id": ANTIFP_ID,
                    "trial_id": row["trial_id"],
                    "arm": "GENERATE",
                    "fix": "before",
                    "score": row["score"],
                    "notes": row["notes"],
                }
            )

    rejects, allows = _iq_gate_selfcheck()
    lookup_ok = lookup_arm_ok(lookup_payload)
    gen_ok = all(gen_arm_ok(p) for p in gen_payloads) and bool(gen_payloads)
    arms_distinct = lookup_ok and gen_ok and all(
        r["classified_arm"] == "GENERATE" for r in gen_rows
    )
    tel_ok = bool(lookup_row.get("mode")) and all(
        r.get("mode") and r.get("wall_ms") is not None for r in gen_rows
    )
    stats = antifp_stats(
        lookup_ok=lookup_ok,
        gen_ok=gen_ok,
        arms_distinct=arms_distinct,
        iq_gate_rejects_lookup_only=rejects,
        iq_gate_allows_dual=allows,
        telemetry_complete=tel_ok,
        n_lookup_trials=1,
        n_gen_trials=len(gen_rows),
    )
    decision = decide_antifp(stats)
    payload = _build_summary(
        decision=decision,
        threads=threads,
        lookup_row=lookup_row,
        gen_rows=gen_rows,
        written=written,
        stats=stats,
    )
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": ANTIFP_ID,
                "decision": decision[:140],
                "cpu_threads": threads,
                "lookup_mode": lookup_row.get("mode"),
                "gen_n": len(gen_rows),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
