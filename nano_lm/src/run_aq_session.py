"""Wave AQ0 SESSION runner (nano:aq:session) — freeze product eval packs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from antifp_ops import classify_arm, extract_telemetry
from aq_session_ops import (
    AQ0_ADV_N,
    AQ0_ADV_PACK,
    AQ0_ID,
    AQ0_LATENCY_PROTOCOL,
    AQ0_MODE_CHARTER,
    AQ0_MODES,
    AQ0_PARA_N,
    AQ0_PARA_PACK,
    AQ0_THESIS,
    adv_kind_counts,
    decide_aq0_session,
    kb_coverage_snapshot,
    map_product_mode,
    para_overlaps_ap_hitl,
)
from curated_sources import SOURCES, source_ids
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads
from z_wrap import load_bank_rows

_OUT = REPO / "results/nano-lm/wave-aq/aq0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-aq/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-aq/error_bank.jsonl"
_Z_BANK = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
_CURATED = REPO / "nano_lm/data/curated"
_PUBLIC = REPO / "docs/results/nano-lm/wave-aq-session.md"
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


def _write_para_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AQ0_PARA_PACK:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AQ0",
            "hyp_id": AQ0_ID,
            "pack": "paraphrase-20",
            "source_id": item["source_id"],
            "parent_question": item["parent_question"],
            "question": item["paraphrase"],
            "gold": item["gold"],
            "status": "frozen",
            "completion": None,
            "score": None,
            "mode": None,
            "wall_ms": None,
            "n_new": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_adv_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AQ0_ADV_PACK:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AQ0",
            "hyp_id": AQ0_ID,
            "pack": "adversary-20",
            "kind": item["kind"],
            "source_id": item["source_id"],
            "question": item["ask"],
            "expect": item["expect"],
            "note": item["note"],
            "status": "frozen",
            "false_hit": None,
            "mode": None,
            "wall_ms": None,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_public_note(*, kb: dict[str, Any], decision: str) -> None:
    para_rows = "\n".join(
        f"| {p['id']} | {p['source_id']} |" for p in AQ0_PARA_PACK
    )
    adv_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['source_id']} |"
        for p in AQ0_ADV_PACK
    )
    holes = "\n".join(f"- {h}" for h in kb.get("holes", []))
    body = "\n".join(
        [
            "# Wave AQ0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-aq/SESSION.md`  ",
            "> Module: `nano_lm/src/aq_session_ops.py` · "
            "Runner: `npm run nano:aq:session`  ",
            "> Parent: [ap-freeze.md](ap-freeze.md) "
            "(Wave AQ reopened explicitly via lab-book reopen 2026-07-27)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze product-science "
            "eval packs (paraphrase-20 · adversary-20 · latency triad · "
            "KB coverage · mode charter). **Not** a CTX/SMART/FAST/APP clone.  ",
            "Packs are **disjoint** from AP-HITL verbatim question text.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| paraphrase-20 | 20 | human rewrites of known golds (AQ1) |",
            "| adversary-20 | 20 | near-miss · OOD · trap (AQ2) |",
            "| latency triad | 3 paths | LOOKUP · PEAK · DECODE p50/p99 (AQ3) |",
            "| KB coverage | snapshot | % + explicit holes (AQ4) |",
            "| mode charter | 3 | UI must show LOOKUP\\|PEAK\\|DECODE (AQ5) |",
            "",
            "## Paraphrase-20 (ids)",
            "",
            "| id | source_id |",
            "|----|-----------|",
            para_rows,
            "",
            "## Adversary-20 (ids)",
            "",
            "| id | kind | source_id |",
            "|----|------|-----------|",
            adv_rows,
            "",
            "## Latency triad protocol",
            "",
            "| Path | Rule |",
            "|------|------|",
            "| LOOKUP | `wall_ms` may be 0 |",
            "| PEAK | `wall_ms` > 0 when claiming gen work; labeled extractive |",
            "| DECODE | `wall_ms` > 0 and `n_new` > 0 |",
            "",
            "Publish p50/p99 in **AQ3 H-LATP**; no silent regress vs FASTBASE hot.",
            "",
            "## Mode charter (anti-FP)",
            "",
            "Every ASK / demo / HITL trial MUST log exactly one of "
            "`LOOKUP` · `PEAK` · `DECODE` (aliases mapped in ops).",
            "",
            "## KB coverage snapshot",
            "",
            f"- curated covered: **{kb.get('covered_n')}** / "
            f"**{kb.get('curated_n')}** ({kb.get('coverage_pct')}%)  ",
            "- complete product KB claim: **forbidden**  ",
            "- holes:",
            holes,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:aq:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-aq/aq0_session.json` · "
            "`results/nano-lm/wave-aq/trials/AQ-*.json`.  ",
            "Contract: `nano_lm/tests/test_aq_session.py`.",
            "",
            "## Claims",
            "",
            "- Product-science packs frozen for Wave AQ — "
            "**not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            "**AF packaged stack + AQ product layer**.  ",
            "- Generative PROMOTE only via later **AQ6 H-NANOGEN** ablated bar.  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · Wave AR invent · "
            "CTX/SMART/FAST/APP clone without named product hole.",
            "",
            "Next: **AQ1 H-PARAHIT** — human paraphrase hit-rate on SEMWRAP.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _smoke_dual_arm() -> dict[str, Any]:
    """LOOKUP wrap + DECODE smoke (anti-FP telemetry + mode charter)."""
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
    l_mode = map_product_mode(str(l_tel["mode"]))
    g_mode = map_product_mode(str(g_tel["mode"]))
    text = str(lookup.get("completion", "")).strip()
    ok = (
        l_arm == "LOOKUP"
        and l_mode == "LOOKUP"
        and l_tel["mode"] == "WRAP_LOOKUP"
        and "def add" in text
        and g_arm == "GENERATE"
        and g_mode == "DECODE"
        and float(g_tel["wall_ms"] or 0) > 0.0
        and int(g_tel["n_new"] or 0) > 0
    )
    return {
        "ok": ok,
        "lookup": {
            "arm": l_arm,
            "raw_mode": l_tel["mode"],
            "product_mode": l_mode,
            "wall_ms": l_tel["wall_ms"],
            "n_new": l_tel["n_new"],
        },
        "decode": {
            "arm": g_arm,
            "raw_mode": g_tel["mode"],
            "product_mode": g_mode,
            "wall_ms": g_tel["wall_ms"],
            "n_new": g_tel["n_new"],
        },
        "modes_charter": sorted(AQ0_MODES),
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


def _hardware() -> tuple[int, int]:
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _build_kb() -> dict[str, Any]:
    curated = set(source_ids())
    bank_rows = load_bank_rows(_Z_BANK)
    bank_srcs = {
        str(r.get("source_id", "")).strip()
        for r in bank_rows
        if str(r.get("source_id", "")).strip()
    }
    return dict(
        kb_coverage_snapshot(curated_ids=curated, bank_source_ids=bank_srcs)
    )


def _freeze_trials(trials_dir: Path) -> tuple[list[str], bool]:
    trials_dir.mkdir(parents=True, exist_ok=True)
    written = _write_para_trials(trials_dir) + _write_adv_trials(trials_dir)
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    ready = trials_dir.is_dir() and len(written) == AQ0_PARA_N + AQ0_ADV_N
    return written, ready


def _check_para_curated(workers: int) -> tuple[list[dict[str, Any]], bool]:
    curated = set(source_ids())
    para_curated = [
        str(p["source_id"])
        for p in AQ0_PARA_PACK
        if str(p["source_id"]) in curated
    ]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        checks = list(pool.map(_curated_path_ok, para_curated))
    ok = all(bool(c["exists"]) for c in checks) if checks else True
    return checks, ok


def _resolve_decision(
    *,
    trials_ready: bool,
    kb: dict[str, Any],
    curated_ok: bool,
) -> tuple[str, list[str]]:
    clash = para_overlaps_ap_hitl()
    decision = decide_aq0_session(trials_dir_ready=trials_ready, kb=kb)
    if clash:
        decision = f"KILL (paraphrase equals AP-HITL: {','.join(clash)})"
    if not curated_ok:
        decision = "KILL (curated blob missing for one or more para source_id)"
    return decision, clash


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    kb = _build_kb()
    curated_checks, curated_ok = _check_para_curated(workers)
    written, trials_ready = _freeze_trials(Path(args.trials_dir))
    decision, clash = _resolve_decision(
        trials_ready=trials_ready, kb=kb, curated_ok=curated_ok
    )
    _write_public_note(kb=kb, decision=decision)
    rc, ask = _run_ask_smoke(decision, skip=bool(args.skip_ask))
    if rc != 0:
        return rc

    payload = {
        "id": AQ0_ID,
        "thesis": AQ0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "para_n": AQ0_PARA_N,
        "adv_n": AQ0_ADV_N,
        "adv_kinds": adv_kind_counts(),
        "latency_protocol": dict(AQ0_LATENCY_PROTOCOL),
        "mode_charter": dict(AQ0_MODE_CHARTER),
        "kb_coverage": kb,
        "prior_ap_overlap": clash,
        "curated_checks": curated_checks,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-aq-session.md",
        "rule": "pesquisa §5 AQ0 · product packs + anti-FP modes",
        "next": "AQ1 H-PARAHIT (paraphrase hit-rate on SEMWRAP)",
        "anti_fp": (
            "LOOKUP|PEAK|DECODE labeled; never LOOKUP-as-IQ; "
            "never peak-as-open-chat; generative bar = AQ6 only"
        ),
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AQ0_ID,
                "decision": decision[:120],
                "cpu_threads": threads,
                "workers": workers,
                "coverage_pct": kb.get("coverage_pct"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
