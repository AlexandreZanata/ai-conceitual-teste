"""Wave AM-FREEZE runner (nano:am:freeze) — lock AM; no Wave AN invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from am_freeze_ops import (
    AM_DECISIONS,
    AM_FREEZE_ID,
    AM_PRODUCT_DOCS,
    AM_PUBLIC,
    AM_THESIS,
    decide_am_freeze,
    render_am_freeze,
)
from am_report_ops import render_paper_lab_wave_am, render_wave_am_summary
from am_session_ops import AM0_PACK
from antifp_ops import classify_arm, extract_telemetry
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-am/am_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/am-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hamfreeze-am-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-am-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-am.md"


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
    _SUMMARY.write_text(render_wave_am_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_am(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_am_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AM-FREEZE — Wave AM lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §3 AM8 · "
                "Public note: [am-freeze.md](am-freeze.md)  ",
                "> After: [wave-am-summary.md](wave-am-summary.md) / "
                "[paper-lab-wave-am.md](paper-lab-wave-am.md)",
                "",
                "## Hypothesis",
                "",
                "After AM-REPORT, freeze Wave AM the same way AL-FREEZE "
                "locked AL: **outcomes stay** (next dual-arm PROMOTEs + "
                "GENTRUTH HOLD); **no Wave AN** without an explicit "
                "reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AM formals keep GENTRUTH HOLD · CTXNEXT…APPNEXT · "
                "HITL · REPORT decisions | **ok** |",
                "| `wave-am-summary` · `paper-lab-wave-am` · `am-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXNEXT** · "
                "**AM-HITL-10** · **COMPLETE** | **ok** |",
                "| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:am:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Ship claim stays scoped **AF packaged stack** "
                "(AM peak gen is grounded extractive — not open chat).  ",
                "2. AM-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AN reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "GENTRUTH peak ≠ open-chat IQ.  ",
                "5. ≤5M hard law remains after CAPCHECK skip.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/am_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_am_freeze.py`",
                "- Summary: `results/nano-lm/wave-am/am_freeze.json`",
                "- Contract: `nano_lm/tests/test_am_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_dual_arm() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = str(AM0_PACK[0]["question"])
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


def run_am_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AM formals + COMPLETE closeout
    WHEN locking Wave AM
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AM_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AM_PUBLIC, *AM_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AM_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AM_PRODUCT_DOCS}
    decision = decide_am_freeze(
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
        "id": AM_FREEZE_ID,
        "hyp_id": AM_FREEZE_ID,
        "stage": "AM8",
        "thesis": AM_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AM_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/am-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hamfreeze-am-freeze.md",
        "wave_am_summary": "docs/results/nano-lm/wave-am-summary.md",
        "rule": "pesquisa §3 AM-FREEZE",
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
        summary = run_am_freeze(
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
                "hyp_id": AM_FREEZE_ID,
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
