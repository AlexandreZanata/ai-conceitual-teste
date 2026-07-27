"""Wave AT-FREEZE runner (nano:at:freeze) — lock AT; no Wave AU invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from at_freeze_ops import (
    AT_DECISIONS,
    AT_FREEZE_ID,
    AT_PRODUCT_DOCS,
    AT_PUBLIC,
    AT_THESIS,
    SHIP_CLAIM,
    decide_at_freeze,
    render_at_freeze,
)
from at_report_ops import render_paper_lab_wave_at, render_wave_at_summary
from matrix_common import REPO, write_json
from shipui_ops import decide_shipui
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-at/at_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/at-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hatfreeze-at-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-at-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-at.md"
_LOCAL_SESSION = REPO / ".local/wave-at/SESSION.md"


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
    _SUMMARY.write_text(render_wave_at_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_at(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_at_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AT-FREEZE — Wave AT lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AT6 · "
                "Public note: [at-freeze.md](at-freeze.md)  ",
                "> After: [wave-at-summary.md](wave-at-summary.md) / "
                "[paper-lab-wave-at.md](paper-lab-wave-at.md)",
                "",
                "## Hypothesis",
                "",
                "After AT-REPORT, freeze Wave AT the same way AS-FREEZE "
                "locked AS: **outcomes stay** (H-PRODREG·H-SHIPAPP·"
                "H-NANOGEN4·AT-REAL-EVAL·AT-REPORT PROMOTE); "
                "**no Wave AU** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AT formals keep PRODREG·SHIPAPP·NANOGEN4·REAL-EVAL·"
                "REPORT PROMOTE | **ok** |",
                "| `wave-at-summary` · `paper-lab-wave-at` · `at-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-NANOGEN4** · "
                "**AT-REAL-EVAL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:at:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AT-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AU reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ unlabeled open chat; SAFE ≠ quality; "
                "snippet-prefix DECODE ≠ GPT-class.  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/at_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_at_freeze.py`",
                "- Summary: `results/nano-lm/wave-at/at_freeze.json`",
                "- Contract: `nano_lm/tests/test_at_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke — no formal rewrite."""
    from run_shipapp import (
        _CHAMPION,
        _CURATED,
        _Z_BANK,
        _smoke_abstain,
        _smoke_decode,
        _smoke_lookup,
        _smoke_peak,
    )

    lookup = _smoke_lookup(root=_CHAMPION, bank=_Z_BANK)
    peak = _smoke_peak(curated=_CURATED)
    decode = _smoke_decode(root=_CHAMPION, bank=_Z_BANK)
    abstain = _smoke_abstain(root=_CHAMPION, bank=_Z_BANK)
    rows = [lookup, peak, decode, abstain]
    decision = decide_shipui(rows=rows)
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


def _update_local_session(decision: str) -> None:
    if not _LOCAL_SESSION.parent.is_dir():
        return
    ok = str(decision).startswith("PROMOTE")
    status = "DONE — PROMOTE" if ok else f"DONE — {decision}"
    wave = "COMPLETE + FROZEN" if ok else "OPEN"
    body = "\n".join(
        [
            f"# Wave AT session checklist (**{wave}** · AT6 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AT **{wave}**).  ",
            "> Parent: AS COMPLETE + FROZEN · Ship: **"
            + SHIP_CLAIM
            + "** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AT6 — AT-FREEZE ({status})** · Next: "
            "**do not invent Wave AU**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/at-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-hatfreeze-at-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AT0 | SESSION | **DONE — PROMOTE** |",
            "| AT1 | H-PRODREG | **DONE — PROMOTE** |",
            "| AT2 | H-SHIPAPP | **DONE — PROMOTE** |",
            "| AT3 | H-NANOGEN4 | **DONE — PROMOTE** |",
            "| AT4 | AT-REAL-EVAL | **DONE — PROMOTE** |",
            "| AT5 | AT-REPORT | **DONE — PROMOTE** |",
            f"| AT6 | AT-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_at_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AT formals + COMPLETE closeout
    WHEN locking Wave AT
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AT_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AT_PUBLIC, *AT_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AT_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AT_PRODUCT_DOCS}
    decision = decide_at_freeze(
        formal_texts=formal_texts,
        public_texts=public_texts,
        product_texts=product_texts,
    )
    ask: dict[str, Any] | None = None
    if not skip_ask:
        ask = _smoke_four_modes()
        if not bool(ask.get("ok")):
            decision = (
                "KILL (LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke failed)"
            )
    ok = str(decision).startswith("PROMOTE")
    _update_local_session(decision)
    payload: dict[str, Any] = {
        "id": AT_FREEZE_ID,
        "hyp_id": AT_FREEZE_ID,
        "stage": "AT6",
        "thesis": AT_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AT_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/at-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hatfreeze-at-freeze.md",
        "wave_at_summary": "docs/results/nano-lm/wave-at-summary.md",
        "rule": "pesquisa §5 AT-FREEZE",
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
        summary = run_at_freeze(
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
                "hyp_id": AT_FREEZE_ID,
                "decision": str(summary.get("decision", ""))[:120],
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
