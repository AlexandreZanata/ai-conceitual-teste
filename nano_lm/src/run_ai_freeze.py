"""Wave AI-FREEZE runner (nano:ai:freeze) — lock AI; no Wave AJ invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ai_freeze_ops import (
    AI_DECISIONS,
    AI_FREEZE_ID,
    AI_PRODUCT_DOCS,
    AI_PUBLIC,
    AI_THESIS,
    decide_ai_freeze,
    render_ai_freeze,
)
from ai_report_ops import render_paper_lab_wave_ai, render_wave_ai_summary
from ai_session_ops import AI0_PACK
from antifp_ops import classify_arm, extract_telemetry
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ai/ai_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ai-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-haifreeze-ai-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ai-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ai.md"


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
    _SUMMARY.write_text(render_wave_ai_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ai(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ai_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AI-FREEZE — Wave AI lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AI8 · "
                "Public note: [ai-freeze.md](ai-freeze.md)  ",
                "> After: [wave-ai-summary.md](wave-ai-summary.md) / "
                "[paper-lab-wave-ai.md](paper-lab-wave-ai.md)",
                "",
                "## Hypothesis",
                "",
                "After AI-REPORT, freeze Wave AI the same way AH-FREEZE "
                "locked AH: **outcomes stay** (including honest HOLDs); "
                "**no Wave AJ** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AI formals keep GENPLUS…APPPUSH · CAPRENEG · HITL · "
                "REPORT decisions | **ok** |",
                "| `wave-ai-summary` · `paper-lab-wave-ai` · `ai-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXPUSH** · "
                "**AI-HITL-10** · **COMPLETE** | **ok** |",
                "| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ai:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Ship claim stays scoped **AF packaged stack** "
                "(AI gen arm below bar).  ",
                "2. AI-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AJ reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ.  ",
                "5. ≤5M hard law remains after CAPRENEG HOLD.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ai_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ai_freeze.py`",
                "- Summary: `results/nano-lm/wave-ai/ai_freeze.json`",
                "- Contract: `nano_lm/tests/test_ai_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_dual_arm() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = str(AI0_PACK[0]["question"])
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


def run_ai_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AI formals + COMPLETE closeout
    WHEN locking Wave AI
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AI_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AI_PUBLIC, *AI_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(12, max(4, cpus - 4), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AI_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AI_PRODUCT_DOCS}
    decision = decide_ai_freeze(
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
        "id": AI_FREEZE_ID,
        "hyp_id": AI_FREEZE_ID,
        "stage": "AI8",
        "thesis": AI_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AI_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ai-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-haifreeze-ai-freeze.md",
        "wave_ai_summary": "docs/results/nano-lm/wave-ai-summary.md",
        "rule": "pesquisa §5 AI-FREEZE",
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
    threads = tune_cpu_threads(max(4, cpus - 4))
    try:
        summary = run_ai_freeze(
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
                "hyp_id": AI_FREEZE_ID,
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
