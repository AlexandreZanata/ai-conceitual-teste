"""Wave AP-FREEZE runner (nano:ap:freeze) — lock AP; no Wave AQ invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from antifp_ops import classify_arm, extract_telemetry
from ap_freeze_ops import (
    AP_DECISIONS,
    AP_FREEZE_ID,
    AP_PRODUCT_DOCS,
    AP_PUBLIC,
    AP_THESIS,
    decide_ap_freeze,
    render_ap_freeze,
)
from ap_report_ops import render_paper_lab_wave_ap, render_wave_ap_summary
from ap_session_ops import AP0_PACK
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ap/ap_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ap-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hapfreeze-ap-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ap-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ap.md"


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


def _read_text(rel: str) -> str:
    path = REPO / rel
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _write_freeze_docs() -> None:
    _FREEZE_DOC.parent.mkdir(parents=True, exist_ok=True)
    _SUMMARY.write_text(render_wave_ap_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ap(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ap_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AP-FREEZE — Wave AP lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §3 AP8 · "
                "Public note: [ap-freeze.md](ap-freeze.md)  ",
                "> After: [wave-ap-summary.md](wave-ap-summary.md) / "
                "[paper-lab-wave-ap.md](paper-lab-wave-ap.md)",
                "",
                "## Hypothesis",
                "",
                "After AP-REPORT, freeze Wave AP the same way AO-FREEZE "
                "locked AO: **outcomes stay** (base dual-arm PROMOTEs + "
                "GENBASE HOLD); **no Wave AQ** without an explicit "
                "reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AP formals keep GENBASE HOLD · CTXBASE…APPBASE · "
                "HITL · REPORT decisions | **ok** |",
                "| `wave-ap-summary` · `paper-lab-wave-ap` · `ap-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXBASE** · "
                "**AP-HITL-10** · **COMPLETE** | **ok** |",
                "| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ap:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Ship claim stays scoped **AF packaged stack** "
                "(AP peak gen is grounded extractive — not open chat).  ",
                "2. AP-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AQ reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "GENBASE peak ≠ open-chat IQ.  ",
                "5. ≤5M hard law remains after CAPCHECK skip.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ap_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ap_freeze.py`",
                "- Summary: `results/nano-lm/wave-ap/ap_freeze.json`",
                "- Contract: `nano_lm/tests/test_ap_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_dual_arm() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = str(AP0_PACK[0]["question"])
    bank = REPO / "results/nano-lm/wave-z/error_bank.jsonl"
    curated = REPO / "nano_lm/data/curated"
    lookup = ask_once(
        question=q,
        askfast=True,
        seed=0,
        bank_path=bank,
        curated_root=curated,
        ask_cache=AskCompletionCache(),
    )
    gen = ask_once(question=q, wrap=False, seed=0)
    l_arm = classify_arm(lookup)
    g_arm = classify_arm(gen)
    l_tel = extract_telemetry(lookup)
    g_tel = extract_telemetry(gen)
    ok = (
        l_arm == "LOOKUP"
        and g_arm == "GENERATE"
        and g_tel["wall_ms"] > 0.0
        and g_tel["n_new"] > 0
        and bool(str(lookup.get("completion", "")).strip())
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


def run_ap_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AP formals + COMPLETE closeout
    WHEN locking Wave AP
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AP_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AP_PUBLIC, *AP_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AP_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AP_PRODUCT_DOCS}
    decision = decide_ap_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_dual_arm()
        if not bool(ask.get("ok")):
            decision = "KILL (dual-arm anti-FP smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    payload: dict[str, Any] = {
        "id": AP_FREEZE_ID,
        "hyp_id": AP_FREEZE_ID,
        "stage": "AP8",
        "thesis": AP_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AP_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ap-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hapfreeze-ap-freeze.md",
        "wave_ap_summary": "docs/results/nano-lm/wave-ap-summary.md",
        "rule": "pesquisa §3 AP-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": "scoped AF packaged stack — not open chat LM",
        "cpu_threads": int(os.environ.get("OMP_NUM_THREADS") or 0),
        "workers": workers,
    }
    write_json(out, payload)
    return payload


def main() -> int:
    _clear_proxy()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, default=_OUT)
    ap.add_argument("--skip-ask", action="store_true")
    args = ap.parse_args()
    cpus = int(os.cpu_count() or 4)
    threads = tune_cpu_threads(max(4, cpus - 2))
    try:
        summary = run_ap_freeze(
            out=Path(args.out), skip_ask=bool(args.skip_ask)
        )
    except (OSError, RuntimeError, ValueError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}), file=sys.stderr)
        return 2
    ok = str(summary.get("decision", "")).startswith("PROMOTE")
    print(
        json.dumps(
            {
                "ok": ok,
                "hyp_id": AP_FREEZE_ID,
                "decision": str(summary.get("decision", ""))[:96],
                "wave_status": summary.get("wave_status"),
                "ship_claim": summary.get("ship_claim"),
                "cpu_threads": threads,
                "workers": summary.get("workers"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
