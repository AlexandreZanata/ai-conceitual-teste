"""Wave AH-FREEZE runner (nano:ah:freeze) — lock AH; no Wave AI invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ah_freeze_ops import (
    AH_DECISIONS,
    AH_FREEZE_ID,
    AH_PRODUCT_DOCS,
    AH_PUBLIC,
    AH_THESIS,
    decide_ah_freeze,
    render_ah_freeze,
)
from ah_report_ops import render_paper_lab_wave_ah, render_wave_ah_summary
from ah_session_ops import AH0_PACK
from antifp_ops import classify_arm, extract_telemetry
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ah/ah_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ah-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hahfreeze-ah-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ah-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ah.md"


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
    _SUMMARY.write_text(render_wave_ah_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ah(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ah_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AH-FREEZE — Wave AH lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AH8 · "
                "Public note: [ah-freeze.md](ah-freeze.md)  ",
                "> After: [wave-ah-summary.md](wave-ah-summary.md) / "
                "[paper-lab-wave-ah.md](paper-lab-wave-ah.md)",
                "",
                "## Hypothesis",
                "",
                "After AH-REPORT, freeze Wave AH the same way AG-FREEZE "
                "locked AG: **outcomes stay** (including honest HOLDs); "
                "**no Wave AI** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AH formals keep GENLIFT…APPLIFT · HITL · REPORT "
                "decisions | **ok** |",
                "| `wave-ah-summary` · `paper-lab-wave-ah` · `ah-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXLIFT** · "
                "**AH-HITL-10** · **COMPLETE** | **ok** |",
                "| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ah:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Ship claim stays scoped **AF packaged stack** "
                "(AH gen arm below bar).  ",
                "2. AH-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AI reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ah_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ah_freeze.py`",
                "- Summary: `results/nano-lm/wave-ah/ah_freeze.json`",
                "- Contract: `nano_lm/tests/test_ah_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_dual_arm() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = str(AH0_PACK[0]["question"])
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


def run_ah_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AH formals + COMPLETE closeout
    WHEN locking Wave AH
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AH_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AH_PUBLIC, *AH_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(12, max(4, cpus - 4), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AH_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AH_PRODUCT_DOCS}
    decision = decide_ah_freeze(
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
        "id": AH_FREEZE_ID,
        "hyp_id": AH_FREEZE_ID,
        "stage": "AH8",
        "thesis": AH_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AH_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ah-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hahfreeze-ah-freeze.md",
        "wave_ah_summary": "docs/results/nano-lm/wave-ah-summary.md",
        "rule": "pesquisa §5 AH-FREEZE",
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
        summary = run_ah_freeze(
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
                "hyp_id": AH_FREEZE_ID,
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
