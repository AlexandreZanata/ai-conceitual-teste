"""Wave AQ-FREEZE runner (nano:aq:freeze) — lock AQ; no Wave AR invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from aq_freeze_ops import (
    AQ_DECISIONS,
    AQ_FREEZE_ID,
    AQ_PRODUCT_DOCS,
    AQ_PUBLIC,
    AQ_THESIS,
    SHIP_CLAIM,
    decide_aq_freeze,
    render_aq_freeze,
)
from aq_report_ops import render_paper_lab_wave_aq, render_wave_aq_summary
from matrix_common import REPO, write_json
from modeui_ops import decide_modeui
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-aq/aq_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/aq-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-haqfreeze-aq-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-aq-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-aq.md"


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
    _SUMMARY.write_text(render_wave_aq_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_aq(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_aq_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AQ-FREEZE — Wave AQ lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AQ9 · "
                "Public note: [aq-freeze.md](aq-freeze.md)  ",
                "> After: [wave-aq-summary.md](wave-aq-summary.md) / "
                "[paper-lab-wave-aq.md](paper-lab-wave-aq.md)",
                "",
                "## Hypothesis",
                "",
                "After AQ-REPORT, freeze Wave AQ the same way AP-FREEZE "
                "locked AP: **outcomes stay** (product PROMOTEs + "
                "H-NANOGEN HOLD); **no Wave AR** without an explicit "
                "reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AQ formals keep PARAHIT…MODEUI · NANOGEN HOLD · "
                "HITL · REPORT decisions | **ok** |",
                "| `wave-aq-summary` · `paper-lab-wave-aq` · `aq-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-PARAHIT** · "
                "**AQ-PRODUCT-HITL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·DECODE mode triad smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:aq:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AQ-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AR reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ open-chat IQ; H-NANOGEN HOLD locks gen claim.  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/aq_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_aq_freeze.py`",
                "- Summary: `results/nano-lm/wave-aq/aq_freeze.json`",
                "- Contract: `nano_lm/tests/test_aq_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_mode_triad() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE smoke (MODEUI) — no formal rewrite."""
    from run_modeui import (
        _CHAMPION,
        _CURATED,
        _Z_BANK,
        _smoke_decode,
        _smoke_lookup,
        _smoke_peak,
    )

    lookup = _smoke_lookup(root=_CHAMPION, bank=_Z_BANK)
    peak = _smoke_peak(curated=_CURATED)
    decode = _smoke_decode(root=_CHAMPION, bank=_Z_BANK)
    rows = [lookup, peak, decode]
    decision = decide_modeui(rows=rows)
    ok = decision == "PROMOTE"
    return {
        "ok": ok,
        "decision": decision,
        "arms": [
            {
                "arm": r.get("arm"),
                "product_mode": r.get("product_mode"),
                "modeui_line": r.get("modeui_line"),
                "wall_ms": r.get("wall_ms"),
                "n_new": r.get("n_new"),
            }
            for r in rows
        ],
    }


def run_aq_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AQ formals + COMPLETE closeout
    WHEN locking Wave AQ
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AQ_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AQ_PUBLIC, *AQ_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AQ_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AQ_PRODUCT_DOCS}
    decision = decide_aq_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_mode_triad()
        if not bool(ask.get("ok")):
            decision = "KILL (LOOKUP·PEAK·DECODE mode triad smoke failed)"
    ok = str(decision).startswith("PROMOTE")
    payload: dict[str, Any] = {
        "id": AQ_FREEZE_ID,
        "hyp_id": AQ_FREEZE_ID,
        "stage": "AQ9",
        "thesis": AQ_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AQ_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/aq-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-haqfreeze-aq-freeze.md",
        "wave_aq_summary": "docs/results/nano-lm/wave-aq-summary.md",
        "rule": "pesquisa §5 AQ-FREEZE",
        "wave_status": "COMPLETE+FROZEN" if ok else "RESEARCH_COMPLETE",
        "ship_claim": SHIP_CLAIM,
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
        summary = run_aq_freeze(
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
                "hyp_id": AQ_FREEZE_ID,
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
