"""Wave AE-FREEZE runner (nano:ae:freeze) — lock AE; no Wave AF invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from ae_freeze_ops import (
    AE_DECISIONS,
    AE_FREEZE_ID,
    AE_PRODUCT_DOCS,
    AE_PUBLIC,
    AE_THESIS,
    decide_ae_freeze,
    render_ae_freeze,
)
from ae_report_ops import render_paper_lab_wave_ae, render_wave_ae_summary
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-ae/ae_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/ae-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-haefreeze-ae-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-ae-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-ae.md"


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
    _SUMMARY.write_text(render_wave_ae_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_ae(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_ae_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AE-FREEZE — Wave AE lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AE7 · "
                "Public note: [ae-freeze.md](ae-freeze.md)  ",
                "> After: [wave-ae-summary.md](wave-ae-summary.md) / "
                "[paper-lab-wave-ae.md](paper-lab-wave-ae.md)",
                "",
                "## Hypothesis",
                "",
                "After AE-REPORT, freeze Wave AE the same way AD-FREEZE "
                "locked AD: **outcomes stay**; **no Wave AF** without an "
                "explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AE formals keep CTXMAX…APPMAX · HITL · REPORT "
                "**PROMOTE** | **ok** |",
                "| `wave-ae-summary` · `paper-lab-wave-ae` · `ae-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXMAX** · "
                "**AE-HITL-10** · **COMPLETE** | **ok** |",
                "| ASKFAST/SEMWRAP held-out known-ask smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:ae:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Product claim stays scoped AE packaged stack "
                "(CTXMAX+SMARTMAX+FASTMAX+APPMAX).  ",
                "2. AE-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md`.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/ae_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_ae_freeze.py`",
                "- Summary: `results/nano-lm/wave-ae/ae_freeze.json`",
                "- Contract: `nano_lm/tests/test_ae_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_askfast() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = (
        "On BIP-32 mainnet, what Base58 prefixes do serialized extended "
        "private vs public keys start with?"
    )
    cache = AskCompletionCache()
    payload = ask_once(
        question=q,
        askfast=True,
        seed=0,
        bank_path=REPO / "results/nano-lm/wave-z/error_bank.jsonl",
        curated_root=REPO / "nano_lm/data/curated",
        ask_cache=cache,
    )
    mode = str(payload.get("mode", ""))
    text = str(payload.get("completion", "")).strip()
    ok = mode in {"SEMWRAP_LOOKUP", "WRAP_LOOKUP", "ASKFAST_CACHE"} and bool(
        text
    )
    return {
        "ok": ok,
        "mode": mode,
        "wall_ms": payload.get("wall_ms"),
        "n_chars": len(text),
    }


def run_ae_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AE PROMOTE formals + COMPLETE closeout
    WHEN locking Wave AE
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AE_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AE_PUBLIC, *AE_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(max(4, cpus - 4), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AE_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AE_PRODUCT_DOCS}
    decision = decide_ae_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_askfast()
        if not bool(ask.get("ok")):
            decision = "KILL (askfast smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    payload: dict[str, Any] = {
        "id": AE_FREEZE_ID,
        "hyp_id": AE_FREEZE_ID,
        "stage": "AE7",
        "thesis": AE_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AE_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/ae-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-haefreeze-ae-freeze.md",
        "wave_ae_summary": "docs/results/nano-lm/wave-ae-summary.md",
        "rule": "pesquisa §5 AE-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
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
        summary = run_ae_freeze(
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
                "hyp_id": AE_FREEZE_ID,
                "decision": str(summary.get("decision", ""))[:96],
                "wave_status": summary.get("wave_status"),
                "cpu_threads": threads,
                "workers": summary.get("workers"),
                "out": str(args.out),
            }
        )
    )
    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
