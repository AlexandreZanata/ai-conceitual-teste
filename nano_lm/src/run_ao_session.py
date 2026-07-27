"""Wave AO0 SESSION runner (nano:ao:session) — freeze held-out HITL×10."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from antifp_ops import classify_arm, extract_telemetry
from ao_session_ops import (
    AO0_ID,
    AO0_N,
    AO0_PACK,
    AO0_THESIS,
    decide_ao0_session,
    missing_pack_source_ids,
    overlaps_prior_questions,
    pack_app_counts,
)
from curated_sources import SOURCES, source_ids
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ao/ao0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-ao/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-ao/error_bank.jsonl"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ao-session.md"
_BY_ID = {str(s["id"]): s for s in SOURCES}


def _curated_path_ok(source_id: str) -> dict[str, Any]:
    meta = _BY_ID.get(source_id, {})
    rel = str(meta.get("path", ""))
    path = _CURATED / rel if rel else Path()
    exists = path.is_file()
    size = int(path.stat().st_size) if exists else 0
    return {
        "source_id": source_id,
        "path": rel,
        "exists": exists,
        "bytes": size,
    }


def _write_frozen_trials(trials_dir: Path) -> list[str]:
    trials_dir.mkdir(parents=True, exist_ok=True)
    written: list[str] = []
    for item in AO0_PACK:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AO0",
            "hyp_id": AO0_ID,
            "app_id": item["app_id"],
            "source_id": item["source_id"],
            "question": item["question"],
            "gold": item["gold"],
            "status": "frozen",
            "completion": None,
            "score": None,
            "error": None,
            "wall_ms": None,
            "mode": None,
            "n_new": None,
            "fix": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_public_note() -> None:
    rows = "\n".join(
        f"| {p['id']} | {p['app_id']} | {p['source_id']} |" for p in AO0_PACK
    )
    body = "\n".join(
        [
            "# Wave AO0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §3 · Session: "
            "`.local/wave-ao/SESSION.md`  ",
            "> Module: `nano_lm/src/ao_session_ops.py` · "
            "Runner: `npm run nano:ao:session`  ",
            "> Parent: [an-freeze.md](an-freeze.md) "
            "(Wave AO reopened explicitly via lab-book reopen 2026-07-27)",
            "",
            "## Decision",
            "",
            "**PROMOTE** — Freeze **10 held-out HITL questions** "
            "(source_id + app_id + gold) for every AO model/stack.  ",
            "Questions are **not** verbatim copies of AB…AN HITL-01…10.  ",
            "Topics: BIP-39 ENT=224 → 21 words · BIP-32 version bytes · "
            "BIP-141 witness program ≤40 · `a.count(x)` · `while` · "
            "`super` · Rust unsigned prefix `u` · `struct` keyword · "
            "REST full block · RFC 791 TTL bits.",
            "",
            "## Mix",
            "",
            "| app_id | Count | Trials |",
            "|--------|------:|--------|",
            "| known-ask | 3 | AO-HITL-01…03 |",
            "| howto | 5 | AO-HITL-04…08 |",
            "| long-doc | 2 | AO-HITL-09…10 |",
            "",
            "## Frozen pack (ids)",
            "",
            "| id | app_id | source_id |",
            "|----|--------|-----------|",
            rows,
            "",
            "## Dual-arm rubric (AO)",
            "",
            "| Arm | Required telemetry | EVAL rule |",
            "|-----|--------------------|-----------|",
            "| LOOKUP | `mode` = WRAP_LOOKUP / SEMWRAP_LOOKUP; "
            "may have `wall_ms=0` | Score completion vs truth; "
            "label honestly — not “model IQ” |",
            "| GENERATE | no wrap **or** miss→decode; "
            "`wall_ms > 0` and `n_new > 0` | Cursor scores completion; "
            "never auto-9 from gold match alone |",
            "",
            "PROMOTE for “smarter/faster model” **forbidden** if only "
            "LOOKUP arm scored.  ",
            "Pass bars (later stages): LOOKUP mean ≥ **7.0** · "
            "GENERATE mean ≥ **5.0** else **HOLD**.  ",
            "Ablation: at least one later stage must report peak-ablated "
            "gen before claiming smarter LM.",
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:ao:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + GENERATE "
            "(`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-ao/ao0_session.json` · "
            "`results/nano-lm/wave-ao/trials/AO-HITL-*.json` · "
            "`error_bank.jsonl`.  ",
            "Contract: `nano_lm/tests/test_ao_session.py`.",
            "",
            "## Claims",
            "",
            "- Held-out scoped app assist HITL set (14th pack) — "
            "**not** open chat LM.  ",
            "- Default ship claim until proven otherwise still "
            "**AF packaged stack**.  ",
            "- Forbidden: QI · STREAM · KVCACHE-Q · GENCACHE · MIXD · "
            "GPFB-K=2 · naive CTX · ZPREF · invent Wave AP · "
            "PROMOTE LOOKUP-only as generative IQ.",
            "",
            "Next: **AO1 H-GENCORE** — smarter usable gen + dual-arm + "
            "ablation gate.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _smoke_dual_arm() -> dict[str, Any]:
    """LOOKUP wrap + GENERATE decode smoke (anti-FP telemetry)."""
    from run_z_ask import ask_once

    known = (
        "Write a short Python function named add that returns "
        "the sum of two integers a and b."
    )
    lookup = ask_once(question=known, wrap=True, seed=0)
    gen = ask_once(question=known, wrap=False, seed=0)
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    text = str(lookup.get("completion", "")).strip()
    ok = (
        l_arm == "LOOKUP"
        and l_tel["mode"] == "WRAP_LOOKUP"
        and "def add" in text
        and g_arm == "GENERATE"
        and float(g_tel["wall_ms"] or 0) > 0.0
        and int(g_tel["n_new"] or 0) > 0
    )
    return {
        "ok": ok,
        "lookup": {
            "arm": l_arm,
            "mode": l_tel["mode"],
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
        },
        "generate": {
            "arm": g_arm,
            "mode": g_tel["mode"],
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
        },
    }


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


def _override_decision(
    decision: str,
    *,
    miss: list[str],
    clash: list[str],
    curated_ok: bool,
) -> str:
    if miss:
        return f"KILL (unknown source_id: {','.join(miss)})"
    if clash:
        return f"KILL (verbatim AB…AN questions: {','.join(clash)})"
    if not curated_ok:
        return "KILL (curated blob missing for one or more source_id)"
    return decision


def _run_ask_smoke(
    decision: str, *, skip: bool
) -> tuple[int, dict[str, Any] | None]:
    if skip or not str(decision).startswith("PROMOTE"):
        return 0, None
    try:
        ask = _smoke_dual_arm()
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2, None
    if not bool(ask.get("ok")):
        print(
            json.dumps(
                {"ok": False, "error": "dual-arm smoke failed", "ask": ask}
            )
        )
        return 2, ask
    return 0, ask


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    # Max hardware without starving the desktop: leave 2 cores free.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))

    known = set(source_ids())
    miss = missing_pack_source_ids(known)
    clash = overlaps_prior_questions()
    ids = [str(p["source_id"]) for p in AO0_PACK]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        curated_checks = list(pool.map(_curated_path_ok, ids))
    curated_ok = all(bool(c["exists"]) for c in curated_checks)

    written = _write_frozen_trials(Path(args.trials_dir))
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    trials_ready = Path(args.trials_dir).is_dir() and len(written) == AO0_N
    _write_public_note()

    decision = _override_decision(
        decide_ao0_session(known_sources=known, trials_dir_ready=trials_ready),
        miss=miss,
        clash=clash,
        curated_ok=curated_ok,
    )
    rc, ask = _run_ask_smoke(decision, skip=bool(args.skip_ask))
    if rc != 0:
        return rc

    payload = {
        "id": AO0_ID,
        "thesis": AO0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "n": AO0_N,
        "app_counts": pack_app_counts(),
        "missing_sources": miss,
        "prior_question_overlap": clash,
        "curated_checks": curated_checks,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-ao-session.md",
        "rule": "pesquisa §3 AO0 · Cursor ASK→EVAL→FIX dual-arm law",
        "next": "AO1 H-GENCORE (smarter gen + ASK dual-arm + ablation)",
        "anti_fp": (
            "LOOKUP arm labeled; generative arm requires wall_ms>0 / "
            "n_new>0; never PROMOTE LOOKUP-only as smarter LM"
        ),
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AO0_ID,
                "decision": decision[:120],
                "cpu_threads": threads,
                "workers": workers,
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
