"""Wave AR0 SESSION runner (nano:ar:session) — freeze product deepen packs."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from antifp_ops import classify_arm, extract_telemetry
from ar_session_ops import (
    AR0_ABSTAIN_PROTOCOL,
    AR0_ADVREG_N,
    AR0_ADVREG_PACK,
    AR0_EXT_N,
    AR0_EXT_PARA_PACK,
    AR0_ID,
    AR0_MODES,
    AR0_NANOGEN2_HYPOTHESIS,
    AR0_NORTH_STAR,
    AR0_SAFE_NOTE,
    AR0_SHIPDEMO_CHARTER,
    AR0_THESIS,
    advreg_kind_counts,
    advreg_overlaps_aq_adv,
    decide_ar0_session,
    ext_overlaps_aq_para,
    map_ar_product_mode,
)
from curated_sources import SOURCES, source_ids
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ar/ar0_session.json"
_TRIALS = REPO / "results/nano-lm/wave-ar/trials"
_ERROR_BANK = REPO / "results/nano-lm/wave-ar/error_bank.jsonl"
_PUBLIC = REPO / "docs/results/nano-lm/wave-ar-session.md"
_LOCAL_SESSION = REPO / ".local/wave-ar/SESSION.md"
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


def _write_ext_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AR0_EXT_PARA_PACK:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AR0",
            "hyp_id": AR0_ID,
            "pack": "external-para-20",
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


def _write_advreg_trials(trials_dir: Path) -> list[str]:
    written: list[str] = []
    for item in AR0_ADVREG_PACK:
        tid = str(item["id"])
        payload = {
            "trial_id": tid,
            "stage": "AR0",
            "hyp_id": AR0_ID,
            "pack": "advreg-20",
            "kind": item["kind"],
            "source_id": item["source_id"],
            "question": item["ask"],
            "expect": item["expect"],
            "note": item["note"],
            "status": "frozen",
            "false_hit": None,
            "mode": None,
            "wall_ms": None,
            "safe_note": AR0_SAFE_NOTE,
        }
        path = trials_dir / f"{tid}.json"
        write_json(path, payload)
        written.append(str(path.relative_to(REPO)))
    return written


def _write_public_note(*, decision: str) -> None:
    ext_rows = "\n".join(
        f"| {p['id']} | {p['source_id']} |" for p in AR0_EXT_PARA_PACK
    )
    adv_rows = "\n".join(
        f"| {p['id']} | {p['kind']} | {p['source_id']} |"
        for p in AR0_ADVREG_PACK
    )
    body = "\n".join(
        [
            "# Wave AR0 — SESSION freeze (**DONE** — PROMOTE)",
            "",
            "> Lab: `.local/pesquisa.md` §5 · Session: "
            "`.local/wave-ar/SESSION.md`  ",
            "> Module: `nano_lm/src/ar_session_ops.py` · "
            "Runner: `npm run nano:ar:session`  ",
            "> Parent: [aq-freeze.md](aq-freeze.md) "
            "(Wave AR reopened explicitly via lab-book reopen 2026-07-27)",
            "",
            "## Decision",
            "",
            f"**{decision.split('(')[0].strip()}** — Freeze product-deepen "
            "packs (external-para-20 · advreg-20 · abstention protocol · "
            "ship-demo charter · NANOGEN2 hypothesis). **Not** a "
            "CTX/SMART/FAST/APP clone.  ",
            "Packs are **disjoint** from AQ-PARA/ADV exact text.",
            "",
            "## Mix",
            "",
            "| Pack | N | Purpose |",
            "|------|--:|---------|",
            "| external-para-20 | 20 | fresh paraphrases ≠ AQ-PARA (AR3) |",
            "| advreg-20 | 20 | adversary regression + SAFE≠quality (AR4) |",
            "| abstention protocol | 1 | DECODE junk → NO_ANSWER/ABSTAIN (AR1) |",
            "| ship-demo charter | 4 modes | LOOKUP\\|PEAK\\|DECODE\\|ABSTAIN (AR2) |",
            "| NANOGEN2 hypothesis | 1 | ablated ≥5.0 generative gate (AR5) |",
            "",
            "## External-para-20 (ids)",
            "",
            "| id | source_id |",
            "|----|-----------|",
            ext_rows,
            "",
            "## Advreg-20 (ids)",
            "",
            "| id | kind | source_id |",
            "|----|------|-----------|",
            adv_rows,
            "",
            "## Abstention protocol",
            "",
            f"- trigger: {AR0_ABSTAIN_PROTOCOL['trigger']}  ",
            f"- action: `{AR0_ABSTAIN_PROTOCOL['action']}` → "
            f"`mode={AR0_ABSTAIN_PROTOCOL['product_mode']}`  ",
            f"- rule: {AR0_ABSTAIN_PROTOCOL['anti_fp']}",
            "",
            "## Ship-demo charter (anti-FP)",
            "",
            "Every ASK / demo / HITL trial MUST log exactly one of "
            "`LOOKUP` · `PEAK` · `DECODE` · `ABSTAIN` "
            "(aliases mapped in ops; `NO_ANSWER` → ABSTAIN).",
            "",
            "## NANOGEN2 hypothesis (one idea)",
            "",
            AR0_NANOGEN2_HYPOTHESIS,
            "",
            "## SAFE ≠ quality",
            "",
            AR0_SAFE_NOTE,
            "",
            "## North star",
            "",
            AR0_NORTH_STAR,
            "",
            "## Validate",
            "",
            "```bash",
            "npm run nano:ar:session",
            "# optional: --skip-ask",
            "npm run nano:test && npm run verify",
            "```",
            "",
            "Dual-arm smoke must keep LOOKUP (`WRAP_LOOKUP`) + DECODE "
            "(`wall_ms>0`, `n_new>0`) on the Z1 add known-ask.  ",
            "Artifacts (gitignored): "
            "`results/nano-lm/wave-ar/ar0_session.json` · "
            "`results/nano-lm/wave-ar/trials/AR-*.json`.  ",
            "Contract: `nano_lm/tests/test_ar_session.py`.",
            "",
            "## Claims",
            "",
            "- Product-deepen packs frozen for Wave AR — "
            "**not** open chat LM.  ",
            "- Ship claim until generative gate clears: "
            "**AF packaged stack + AQ product layer**.  ",
            "- Generative PROMOTE only via later **AR5 H-NANOGEN2** "
            "ablated bar ≥5.0.  ",
            "- Forbidden: LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "mini-AGI claim early · Wave AS invent · CTX/SMART/FAST/APP clone "
            "without named product hole.",
            "",
            "Next: **AR1 H-ABSTAIN** — refuse junk DECODE → NO_ANSWER/ABSTAIN.",
            "",
        ]
    )
    _PUBLIC.parent.mkdir(parents=True, exist_ok=True)
    _PUBLIC.write_text(body, encoding="utf-8")


def _smoke_dual_arm() -> dict[str, Any]:
    """LOOKUP wrap + DECODE smoke (anti-FP telemetry + AR mode charter)."""
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
    l_mode = map_ar_product_mode(str(l_tel["mode"]))
    g_mode = map_ar_product_mode(str(g_tel["mode"]))
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
        "modes_charter": sorted(AR0_MODES),
        "abstain_alias": map_ar_product_mode("NO_ANSWER"),
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
    # Max safe: leave 2 cores free; avoid thrashing with ~10Gi avail RAM.
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    workers = min(14, max(4, cpus - 2))
    return threads, workers


def _freeze_trials(trials_dir: Path) -> tuple[list[str], bool]:
    trials_dir.mkdir(parents=True, exist_ok=True)
    written = _write_ext_trials(trials_dir) + _write_advreg_trials(trials_dir)
    _ERROR_BANK.parent.mkdir(parents=True, exist_ok=True)
    if not _ERROR_BANK.is_file():
        _ERROR_BANK.write_text("", encoding="utf-8")
    ready = trials_dir.is_dir() and len(written) == AR0_EXT_N + AR0_ADVREG_N
    return written, ready


def _check_ext_curated(workers: int) -> tuple[list[dict[str, Any]], bool]:
    curated = set(source_ids())
    ext_curated = [
        str(p["source_id"])
        for p in AR0_EXT_PARA_PACK
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
    clash_aq = ext_overlaps_aq_para()
    clash_adv = advreg_overlaps_aq_adv()
    decision = decide_ar0_session(
        trials_dir_ready=trials_ready, north_star_signed=True
    )
    if clash_aq:
        decision = f"KILL (ext-para equals AQ-PARA: {','.join(clash_aq)})"
    if clash_adv:
        decision = f"KILL (advreg equals AQ-ADV: {','.join(clash_adv)})"
    if not curated_ok:
        decision = "KILL (curated blob missing for one or more ext source_id)"
    return decision, clash_aq, clash_adv


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    status = "DONE — PROMOTE" if decision.startswith("PROMOTE") else "KILL"
    body = "\n".join(
        [
            f"# Wave AR session checklist (**OPEN** · AR0 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            "(Wave AR **OPEN** · Product Science deepen + Nano Generative).  ",
            "> Parent: AQ COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.  ",
            "> Reopen: 2026-07-27 — explicit lab-book reopen after AQ-FREEZE.",
            "",
            "## Current stage",
            "",
            f"**AR0 — SESSION ({status})** · Next: **AR1 H-ABSTAIN**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            "| Wave | **AR OPEN** |",
            "| Track | Caminho A deepen (abstain · ship demo · paraext · "
            "advreg) + **H-NANOGEN2** north star |",
            "| Parent | AQ COMPLETE + FROZEN (H-NANOGEN HOLD 4.0) |",
            "| Open hole | abstention UX · ship demo · external para · "
            "ablated gen ≥5 |",
            "| Forbidden | LOOKUP-as-IQ · peak-as-open-chat · SAFE-as-quality · "
            "mini-AGI claim early · Wave AS invent · ≤5M raise without CAPCHECK |",
            "",
            "## North star (signed)",
            "",
            AR0_NORTH_STAR,
            "",
            "## Cursor operator checklist (AR0)",
            "",
            "```text",
            "MODEL = AR0-SESSION",
            "",
            "[x] Freeze external-para pack (≠ AQ-PARA exact text)",
            "[x] Freeze abstention protocol (DECODE junk → ABSTAIN / NO_ANSWER)",
            "[x] Charter ship/demo UI modes: LOOKUP | PEAK | DECODE | ABSTAIN",
            "[x] Write NANOGEN2 hypothesis (how to beat ablated 4.0) — one idea",
            "[x] Adversary regression pack + SAFE≠quality note in outputs",
            "[x] Do NOT open CTX/SMART/FAST/APP clone stages",
            "[ ] Next: AR1 H-ABSTAIN (or AR2 H-SHIPDEMO if demo unblocks eval)",
            "```",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            f"| AR0 | SESSION | **{status}** |",
            "| AR1 | H-ABSTAIN | **NEXT** |",
            "| AR2 | H-SHIPDEMO | pending |",
            "| AR3 | H-PARAEXT | pending |",
            "| AR4 | H-ADVREG | pending |",
            "| AR5 | H-NANOGEN2 | pending (generative north-star gate) |",
            "| AR6 | AR-DUAL-HITL | pending |",
            "| AR7 | AR-REPORT | pending |",
            "| AR8 | AR-FREEZE | pending |",
            "",
            "## Metrics board (fill as stages run)",
            "",
            "| Metric | Target | Current |",
            "|--------|--------|---------|",
            "| External paraphrase hit (PARAEXT) | ≥ bar (set in AR3) | "
            "AQ PARAHIT 0.95 baseline |",
            "| Adversary false-hit | **0** | AQ 0/20 |",
            "| Abstention on OOD/miss | ↑ vs garbage DECODE | protocol frozen |",
            "| Latency p50/p99 triad (+ ABSTAIN) | publish | AQ LATP baseline |",
            "| Ship demo modes visible | 4/4 incl. ABSTAIN | charter frozen |",
            "| Ablated gen mean (NANOGEN2) | ≥ **5.0** to PROMOTE | "
            "**4.0 HOLD** |",
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
    decision, clash_aq, clash_adv = _resolve_decision(
        trials_ready=trials_ready, curated_ok=curated_ok
    )
    _write_public_note(decision=decision)
    _update_local_session(decision)
    rc, ask = _run_ask_smoke(decision, skip=bool(args.skip_ask))
    if rc != 0:
        return rc

    payload = {
        "id": AR0_ID,
        "thesis": AR0_THESIS,
        "decision": decision,
        "cpu_threads": threads,
        "workers": workers,
        "ext_n": AR0_EXT_N,
        "advreg_n": AR0_ADVREG_N,
        "advreg_kinds": advreg_kind_counts(),
        "abstain_protocol": dict(AR0_ABSTAIN_PROTOCOL),
        "shipdemo_charter": dict(AR0_SHIPDEMO_CHARTER),
        "nanogen2_hypothesis": AR0_NANOGEN2_HYPOTHESIS,
        "safe_note": AR0_SAFE_NOTE,
        "north_star": AR0_NORTH_STAR,
        "prior_aq_para_overlap": clash_aq,
        "prior_aq_adv_overlap": clash_adv,
        "curated_checks": curated_checks,
        "trials_written": written,
        "error_bank": str(_ERROR_BANK.relative_to(REPO)),
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/wave-ar-session.md",
        "rule": "pesquisa §5 AR0 · product deepen + anti-FP ABSTAIN",
        "next": "AR1 H-ABSTAIN (refuse junk DECODE → NO_ANSWER)",
        "anti_fp": (
            "LOOKUP|PEAK|DECODE|ABSTAIN labeled; never LOOKUP-as-IQ; "
            "never peak-as-open-chat; SAFE≠quality; generative bar = AR5 only"
        ),
    }
    write_json(Path(args.out), payload)
    ok = str(decision).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AR0_ID,
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
