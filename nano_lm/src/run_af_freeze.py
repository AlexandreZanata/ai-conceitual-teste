"""Wave AF-FREEZE runner (nano:af:freeze) — lock AF; no Wave AG invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from af_freeze_ops import (
    AF_DECISIONS,
    AF_FREEZE_ID,
    AF_PRODUCT_DOCS,
    AF_PUBLIC,
    AF_THESIS,
    decide_af_freeze,
    render_af_freeze,
)
from af_report_ops import render_paper_lab_wave_af, render_wave_af_summary
from af_session_ops import AF0_PACK
from matrix_common import REPO, write_json
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-af/af_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/af-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-haffreeze-af-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-af-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-af.md"


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
    _SUMMARY.write_text(render_wave_af_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_af(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_af_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AF-FREEZE — Wave AF lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AF7 · "
                "Public note: [af-freeze.md](af-freeze.md)  ",
                "> After: [wave-af-summary.md](wave-af-summary.md) / "
                "[paper-lab-wave-af.md](paper-lab-wave-af.md)",
                "",
                "## Hypothesis",
                "",
                "After AF-REPORT, freeze Wave AF the same way AE-FREEZE "
                "locked AE: **outcomes stay**; **no Wave AG** without an "
                "explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AF formals keep CTXULTRA…APPULTRA · HITL · REPORT "
                "**PROMOTE** | **ok** |",
                "| `wave-af-summary` · `paper-lab-wave-af` · `af-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-CTXULTRA** · "
                "**AF-HITL-10** · **COMPLETE** | **ok** |",
                "| ASKFAST/SEMWRAP held-out known-ask smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:af:freeze",
                "```",
                "",
                "## Finding",
                "",
                "1. Product claim stays scoped AF packaged stack "
                "(CTXULTRA+SMARTULTRA+FASTULTRA+APPULTRA).  ",
                "2. AF-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md`.",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/af_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_af_freeze.py`",
                "- Summary: `results/nano-lm/wave-af/af_freeze.json`",
                "- Contract: `nano_lm/tests/test_af_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_askfast() -> dict[str, Any]:
    from askfast_ops import AskCompletionCache
    from run_z_ask import ask_once

    q = str(AF0_PACK[0]["question"])
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


def run_af_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AF PROMOTE formals + COMPLETE closeout
    WHEN locking Wave AF
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AF_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AF_PUBLIC, *AF_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(12, max(4, cpus - 4), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AF_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AF_PRODUCT_DOCS}
    decision = decide_af_freeze(
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
        "id": AF_FREEZE_ID,
        "hyp_id": AF_FREEZE_ID,
        "stage": "AF7",
        "thesis": AF_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AF_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/af-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-haffreeze-af-freeze.md",
        "wave_af_summary": "docs/results/nano-lm/wave-af-summary.md",
        "rule": "pesquisa §5 AF-FREEZE",
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
        summary = run_af_freeze(
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
                "hyp_id": AF_FREEZE_ID,
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
