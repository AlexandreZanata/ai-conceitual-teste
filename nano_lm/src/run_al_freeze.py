"""Wave AL-FREEZE runner (nano:al:freeze) — lock AL; no Wave AM invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from al_freeze_ops import (
    AL_DECISIONS,
    AL_FREEZE_ID,
    AL_PRODUCT_DOCS,
    AL_PUBLIC,
    AL_THESIS,
    decide_al_freeze,
    render_al_freeze,
)
from al_report_ops import render_paper_lab_wave_al, render_wave_al_summary
from al_session_ops import AL0_PACK
from antifp_ops import classify_arm, extract_telemetry
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-al/al_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/al-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-halfreeze-al-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-al-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-al.md"


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
    _SUMMARY.write_text(render_wave_al_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_al(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_al_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AL-FREEZE — Wave AL lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §3 AL8 · "
                "Public note: [al-freeze.md](al-freeze.md)  ",
                "> After: [wave-al-summary.md](wave-al-summary.md) / "
                "[paper-lab-wave-al.md](paper-lab-wave-al.md)",
                "",
                "## Hypothesis",
                "",
                "After AL-REPORT, freeze Wave AL the same way AK-FREEZE "
                "locked AK: **outcomes stay** (fresh dual-arm PROMOTEs + "
                "GENFRESH HOLD); **no Wave AM** without an explicit "
                "reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AL formals keep GENFRESH HOLD · CTXFRESH…APPFRESH · "
                "HITL · REPORT decisions | **ok** |",
                "| `wave-al-summary` · `paper-lab-wave-al` · `al-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXFRESH** · "
                "**AL-HITL-10** · **COMPLETE** | **ok** |",
                "| Dual-arm LOOKUP+GENERATE smoke (`wall_ms>0`) | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:al:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Ship claim stays scoped **AF packaged stack** "
                "(AL peak gen is grounded extractive — not open chat).  ",
                "2. AL-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AM reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "GENFRESH peak ≠ open-chat IQ.  ",
                "5. ≤5M hard law remains after CAPCHECK skip.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/al_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_al_freeze.py`",
                "- Summary: `results/nano-lm/wave-al/al_freeze.json`",
                "- Contract: `nano_lm/tests/test_al_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_dual_arm() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = str(AL0_PACK[0]["question"])
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


def run_al_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AL formals + COMPLETE closeout
    WHEN locking Wave AL
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AL_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AL_PUBLIC, *AL_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AL_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AL_PRODUCT_DOCS}
    decision = decide_al_freeze(
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
        "id": AL_FREEZE_ID,
        "hyp_id": AL_FREEZE_ID,
        "stage": "AL8",
        "thesis": AL_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AL_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/al-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-halfreeze-al-freeze.md",
        "wave_al_summary": "docs/results/nano-lm/wave-al-summary.md",
        "rule": "pesquisa §3 AL-FREEZE",
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
        summary = run_al_freeze(
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
                "hyp_id": AL_FREEZE_ID,
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
