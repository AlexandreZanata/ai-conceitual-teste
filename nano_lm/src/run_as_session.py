"""Wave AS0 SESSION runner (nano:as:session) — freeze product-trust packs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from antifp_ops import classify_arm, extract_telemetry
from as_session_ops import (
    AS0_ADVSAFE_N,
    AS0_ADVSAFE_PACK,
    AS0_ANTI_FP,
    AS0_ASKABSTAIN_CHARTER,
    AS0_ID,
    AS0_METRICS_PROTOCOL,
    AS0_MODES,
    AS0_NANOGEN3_HYPOTHESIS,
    AS0_NORTH_STAR,
    AS0_PARA_N,
    AS0_PARAEXT2_PACK,
    AS0_REQUIRED_ADV_PARENTS,
    AS0_SAFE_NOTE,
    AS0_SEMFIX_HYPOTHESIS,
    AS0_THESIS,
    advsafe_cited_parents,
    advsafe_kind_counts,
    decide_as0_session,
    map_as_product_mode,
    paraext2_overlaps_aq_para,
    paraext2_overlaps_ar_ext,
)
from curated_sources import SOURCES, source_ids
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-as/as0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-as/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-as/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-as-session.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"
_CURATED = REPO / "nano_lm/data/curated"
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
    for item in AS0_PARAEXT2_PACK:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AS0",
            "hyp_id": AS0_ID,
            "pack": "paraext2-20",
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


def _write_advsafe_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AS0_ADVSAFE_PACK:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AS0",
            "hyp_id": AS0_ID,
            "pack": "advsafe-20",
            "kind": item["kind"],
            "source_id": item["source_id"],
            "parent_id": item.get("parent_id"),
            "question": item["ask"],
            "expect": item["expect"],
            "note": item["note"],
            "status": "frozen",
            "false_hit": None,
            "mode": None,
            "wall_ms": None,
            "safe_note": AS0_SAFE_NOTE,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_public_note(*, decision: str) -> None:
    para_rows = "\n".join(
        f"| {p['id']} | {p['source_id']} |" for p in AS0_PARAEXT2_PACK
    )
    adv_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p.get('parent_id', '—')} | "
        f"{p['source_id']} |"
        for p in AS0_ADVSAFE_PACK
    )
    body = "\n".join(
        [
            "# Wave AS0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-as/SESSION.md`  ",
            "> Module: `nano_lm/src/as_session_ops.py` · "
            "Runner: `npm run nano:as:session`  ",
            "> Parent: [ar-freeze.md](ar-freeze.md) "
            "(Wave AS reopened explicitly via lab-book reopen 2026-07-27)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze product-trust "
            "packs (ADVSAFE-20 citing AR-ADVREG-01/05 · PARAEXT2-20 · "
            "ASKABSTAIN charter · SEMFIX hyp · NANOGEN3 hyp · metrics "
            "protocol). **Not** a CTX/SMART/FAST/APP clone.  ",
            "PARAEXT2 paraphrases are **disjoint** from AQ-PARA and AR-EXT "
            "exact text. Anti-FP signed.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| ADVSAFE-20 | 20 | adversary reopen; cite AR-ADVREG-01/05 "
            "(AS3) |",
            "| PARAEXT2-20 | 20 | fresh paraphrases ≠ AQ/AR-EXT (AS4) |",
            "| ASKABSTAIN charter | 1 | default `nano:z:ask` → ABSTAIN "
            "(AS1) |",
            "| SEMFIX hypothesis | 1 | negation/contrast/margin (AS2) |",
            "| metrics protocol | 1 | p50/p99 + KB holes (AS5) |",
            "| NANOGEN3 hypothesis | 1 | ablated ≥5.0 generative gate "
            "(AS7) |",
            "",
            "## PARAEXT2-20 (ids)",
            "",
            "| id | source_id |",
            "|----|-----------|",
            para_rows,
            "",
            "## ADVSAFE-20 (ids)",
            "",
            "| id | kind | parent_id | source_id |",
            "|----|------|-----------|-----------|",
            adv_rows,
            "",
            "## Required parent citations",
            "",
            ", ".join(sorted(AS0_REQUIRED_ADV_PARENTS)),
            "",
            "## ASKABSTAIN charter",
            "",
            f"- paths: `{AS0_ASKABSTAIN_CHARTER['paths']}`  ",
            f"- trigger: {AS0_ASKABSTAIN_CHARTER['trigger']}  ",
            f"- action: `{AS0_ASKABSTAIN_CHARTER['action']}` → "
            f"`mode={AS0_ASKABSTAIN_CHARTER['product_mode']}`  ",
            f"- rule: {AS0_ASKABSTAIN_CHARTER['anti_fp']}",
            "",
            "## SEMFIX hypothesis (one idea)",
            "",
            AS0_SEMFIX_HYPOTHESIS,
            "",
            "## NANOGEN3 hypothesis (one idea)",
            "",
            AS0_NANOGEN3_HYPOTHESIS,
            "",
            "## Metrics protocol",
            "",
            f"- paths: {' · '.join(AS0_METRICS_PROTOCOL['paths'])}  ",
            f"- metrics: {', '.join(AS0_METRICS_PROTOCOL['metrics'])}  ",
            f"- KB: {', '.join(AS0_METRICS_PROTOCOL['kb'])}  ",
            "- complete product-KB claim forbidden",
            "",
            "## SAFE ≠ quality",
            "",
            AS0_SAFE_NOTE,
            "",
            "## Anti-FP (signed)",
            "",
            AS0_ANTI_FP,
            "",
            "## North star",
            "",
            AS0_NORTH_STAR,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:as:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-as/as0_session.json` · "
            "`results/nano-lm/wave-as/trials/AS-*.json`.  ",
            "Contract: `nano_lm/tests/test_as_session.py`.",
            "",
            "## Claims",
            "",
            "- Product-trust packs frozen for Wave AS — "
            "**not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            "**AF packaged stack + AQ product layer**.  ",
            "- Generative PROMOTE only via later **AS7 H-NANOGEN3** "
            "ablated bar ≥5.0.  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "mini-AGI claim early · Wave AT invent · CTX/SMART/FAST/APP clone "
            "without named product hole · bank stuffing.",
            "",
            "Next: **AS1 H-ASKABSTAIN** — wire ABSTAIN into default "
            "`nano:z:ask` / apps.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _smoke_dual_arm() -> dict[str, Any]:
    """LOOKUP wrap + DECODE smoke (anti-FP telemetry + AS mode charter)."""
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
    l_mode = map_as_product_mode(str(l_tel["mode"]))
    g_mode = map_as_product_mode(str(g_tel["mode"]))
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
        "modes_charter": sorted(AS0_MODES),
        "abstain_alias": map_as_product_mode("NO_ANSWER"),
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
    # Max safe: leave 2 cores free; ~10Gi available RAM — avoid thrashing.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _freeze_trials(trials_dir: Path) -> tuple[list[str], bool]:
    trials_dir.mkdir(parents=True, exist_ok=True)
    written = _write_para_trials(trials_dir) + _write_advsafe_trials(
        trials_dir
    )
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    ready = trials_dir.is_dir() and len(written) == AS0_PARA_N + AS0_ADVSAFE_N
    return written, ready


def _check_ext_curated(workers: int) -> tuple[list[dict[str, Any]], bool]:
    curated = set(source_ids())
    ext_curated = [
        str(p["source_id"])
        for p in AS0_PARAEXT2_PACK
        if str(p["source_id"]) in curated
    ]
    with ThreadPoolExecutor(max_workers=workers) as pool:
        checks = list(pool.map(_curated_path_ok, ext_curated))
    ok = all(bool(c["exists"]) for c in checks) if checks else True
    return checks, ok


def _resolve_decision(
    *,
    trials_ready: bool,
    curated_ok: bool,
) -> tuple[str, list[str], list[str]]:
    clash_aq = paraext2_overlaps_aq_para()
    clash_ar = paraext2_overlaps_ar_ext()
    decision = decide_as0_session(
        trials_dir_ready=trials_ready, anti_fp_signed=True
    )
    if clash_aq:
        decision = f"KILL (paraext2 equals AQ-PARA: {','.join(clash_aq)})"
    if clash_ar:
        decision = f"KILL (paraext2 equals AR-EXT: {','.join(clash_ar)})"
    if not curated_ok:
        decision = "KILL (curated blob missing for one or more ext source_id)"
    return decision, clash_aq, clash_ar


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision.startswith("PROMOTE") else "KILL"
    body = "\n".join(
        [
            f"# Wave AS session checklist (**OPEN** · AS0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AS **OPEN** · Product Science fix + Nano Generative).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.  ",
            "> Reopen: 2026-07-27 — explicit after AR-FREEZE "
            "(ADVREG KILL · PARAEXT HOLD · NANOGEN2 HOLD · "
            "abstain not on default ask).",
            "",
            "## Current stage",
            "",
            f"**AS0 — SESSION ({status})** · Next: **AS1 H-ASKABSTAIN**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AS OPEN** |",
            "| Track | Caminho A fix (ASKABSTAIN · SEMFIX · ADVSAFE · "
            "PARAEXT2 · METRICS · SHIPUI) + **H-NANOGEN3** |",
            "| Parent | AR COMPLETE + FROZEN |",
            "| Open hole | default-ask abstain · SEMWRAP near-miss FH · "
            "paraext≥0.7 · ablated≥5 |",
            "| Forbidden | LOOKUP-as-IQ · mini-AGI early · Wave AT invent · "
            "≤5M raise without CAPCHECK · bank stuffing |",
            "",
            "## North star (signed)",
            "",
            AS0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AS0)",
            "",
            "```text",
            "MODEL = AS0-SESSION",
            "",
            "[x] Freeze ADVSAFE pack including AR-ADVREG-01 / AR-ADVREG-05 "
            "reproductions",
            "[x] Freeze PARAEXT2 pack (≠ AQ-PARA / ≠ AR-EXT exact text)",
            "[x] Charter ASKABSTAIN: default nano:z:ask / apps must ABSTAIN "
            "junk DECODE",
            "[x] Write SEMFIX hypothesis (negation · contrast · margin) — "
            "one idea",
            "[x] Write NANOGEN3 hypothesis — one idea to beat ablated 4.3",
            "[x] Metrics protocol: p50/p99 LOOKUP|PEAK|DECODE|ABSTAIN + "
            "KB holes",
            "[x] Do NOT open CTX/SMART/FAST/APP clones",
            "[ ] Next: AS1 H-ASKABSTAIN",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AS0 | SESSION | **{status}** |",
            "| AS1 | H-ASKABSTAIN | **NEXT** |",
            "| AS2 | H-SEMFIX | pending |",
            "| AS3 | H-ADVSAFE | pending |",
            "| AS4 | H-PARAEXT2 | pending |",
            "| AS5 | H-METRICS | pending |",
            "| AS6 | H-SHIPUI | pending |",
            "| AS7 | H-NANOGEN3 | pending (generative north-star gate) |",
            "| AS8 | AS-DUAL-HITL | pending |",
            "| AS9 | AS-REPORT | pending |",
            "| AS10 | AS-FREEZE | pending |",
            "",
            "## Metrics board",
            "",
            "| Metric | Target | Baseline |",
            "|--------|--------|----------|",
            "| Default-ask OOD abstain | → NO_ANSWER | raw `z:ask` still "
            "dumps junk |",
            "| Adversary / near-miss FH | **0** | AR ADVREG **2**/20 KILL |",
            "| External paraphrase hit | ≥ **0.70** | AR PARAEXT **0.65** "
            "HOLD |",
            "| Latency p50/p99 | publish | AQ LATP |",
            "| KB coverage + holes | publish | AQ 22/22 + 6 holes |",
            "| Modes on ask/demo | 4/4 | shipdemo only |",
            "| Ablated gen (NANOGEN3) | ≥ **5.0** | NANOGEN2 **4.3** HOLD |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--trials-dir", type=Path, default=_TRIALS)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()

    threads, workers = _hardware()
    curated_checks, curated_ok = _check_ext_curated(workers)
    written, trials_ready = _freeze_trials(Path(args.trials_dir))
    decision, clash_aq, clash_ar = _resolve_decision(
        trials_ready=trials_ready, curated_ok=curated_ok
    )
    _write_public_note(decision=decision)
    _update_local_session(decision)
    rc, ask = _run_ask_smoke(decision, skip=bool(args.skip_ask))
    if rc != 0:
        return rc

    payload = {
        "id": AS0_ID,
        "thesis": AS0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "para_n": AS0_PARA_N,
        "advsafe_n": AS0_ADVSAFE_N,
        "advsafe_kinds": advsafe_kind_counts(),
        "advsafe_parents": sorted(advsafe_cited_parents()),
        "required_adv_parents": sorted(AS0_REQUIRED_ADV_PARENTS),
        "askabstain_charter": dict(AS0_ASKABSTAIN_CHARTER),
        "semfix_hypothesis": AS0_SEMFIX_HYPOTHESIS,
        "nanogen3_hypothesis": AS0_NANOGEN3_HYPOTHESIS,
        "metrics_protocol": dict(AS0_METRICS_PROTOCOL),
        "safe_note": AS0_SAFE_NOTE,
        "anti_fp": AS0_ANTI_FP,
        "north_star": AS0_NORTH_STAR,
        "prior_aq_para_overlap": clash_aq,
        "prior_ar_ext_overlap": clash_ar,
        "curated_checks": curated_checks,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-as-session.md",
        "rule": "pesquisa §5 AS0 · product trust + anti-FP ASKABSTAIN",
        "next": "AS1 H-ASKABSTAIN (wire ABSTAIN into default nano:z:ask)",
        "anti_fp_signed": True,
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AS0_ID,
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
