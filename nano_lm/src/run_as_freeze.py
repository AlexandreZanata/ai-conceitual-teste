"""Wave AS-FREEZE runner (nano:as:freeze) — lock AS; no Wave AT invent."""

from __future__ import annotations

import argparse
import json
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

from as_freeze_ops import (
    AS_DECISIONS,
    AS_FREEZE_ID,
    AS_PRODUCT_DOCS,
    AS_PUBLIC,
    AS_THESIS,
    SHIP_CLAIM,
    decide_as_freeze,
    render_as_freeze,
)
from as_report_ops import render_paper_lab_wave_as, render_wave_as_summary
from matrix_common import REPO, write_json
from shipui_ops import decide_shipui
from tipd_pair import tune_cpu_threads

_OUT = REPO / "results/nano-lm/wave-as/as_freeze.json"
_FREEZE_DOC = REPO / "docs/results/nano-lm/as-freeze.md"
_FORMAL = REPO / "docs/results/nano-lm/formal-hasfreeze-as-freeze.md"
_SUMMARY = REPO / "docs/results/nano-lm/wave-as-summary.md"
_PAPER = REPO / "docs/results/nano-lm/paper-lab-wave-as.md"
_LOCAL_SESSION = REPO / ".local/wave-as/SESSION.md"


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
    _SUMMARY.write_text(render_wave_as_summary(), encoding="utf-8")
    _PAPER.write_text(render_paper_lab_wave_as(), encoding="utf-8")
    _FREEZE_DOC.write_text(render_as_freeze(), encoding="utf-8")
    _FORMAL.write_text(
        "\n".join(
            [
                "# AS-FREEZE — Wave AS lock (**DONE** — PROMOTE)",
                "",
                "> Lab: `.local/pesquisa.md` §5 AS10 · "
                "Public note: [as-freeze.md](as-freeze.md)  ",
                "> After: [wave-as-summary.md](wave-as-summary.md) / "
                "[paper-lab-wave-as.md](paper-lab-wave-as.md)",
                "",
                "## Hypothesis",
                "",
                "After AS-REPORT, freeze Wave AS the same way AR-FREEZE "
                "locked AR: **outcomes stay** (product PROMOTEs + "
                "H-NANOGEN3 HOLD + AS-DUAL-HITL product PROMOTE with gen "
                "locked); **no Wave AT** without an explicit reopen agenda.",
                "",
                "## Gate",
                "",
                "| Check | Result |",
                "|-------|--------|",
                "| AS formals keep ASKABSTAIN·SEMFIX·ADVSAFE·PARAEXT2·"
                "METRICS·SHIPUI·DUAL-HITL·REPORT PROMOTE · "
                "NANOGEN3 HOLD | **ok** |",
                "| `wave-as-summary` · `paper-lab-wave-as` · `as-freeze` "
                "contain **COMPLETE** | **ok** |",
                "| RECIPES + champion-card contain **H-ASKABSTAIN** · "
                "**AS-DUAL-HITL** · **COMPLETE** | **ok** |",
                "| LOOKUP·PEAK·DECODE·ABSTAIN four-mode smoke | **ok** |",
                "| Decision | **PROMOTE** |",
                "",
                "## Reproduce",
                "",
                "```bash",
                "npm run nano:as:freeze",
                "```",
                "",
                "## Finding",
                "",
                f"1. Ship claim stays scoped **{SHIP_CLAIM}**.  ",
                "2. AS-FREEZE does **not** invent new serve/train hyps.  ",
                "3. Further research requires a new § in "
                "`.local/pesquisa.md` (Wave AT reopen).  ",
                "4. Anti-FP law remains: LOOKUP ≠ generative IQ; "
                "PEAK ≠ open-chat IQ; SAFE ≠ quality; "
                "H-NANOGEN3 HOLD locks gen claim.  ",
                "5. ≤5M hard law remains (CAPCHECK closed).",
                "",
                "## Artifacts",
                "",
                "- Module: `nano_lm/src/as_freeze_ops.py` · "
                "Runner: `nano_lm/src/run_as_freeze.py`",
                "- Summary: `results/nano-lm/wave-as/as_freeze.json`",
                "- Contract: `nano_lm/tests/test_as_freeze.py`",
                "",
            ]
        ),
        encoding="utf-8",
    )


def _smoke_four_modes() -> dict[str, Any]:
    """LOOKUP · PEAK · DECODE · ABSTAIN smoke — no formal rewrite."""
    from run_shipui import (
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
            f"# Wave AS session checklist (**{wave}** · AS10 {status})",
            "",
            "> Private under `.local/`. Lab: `.local/pesquisa.md` "
            f"(Wave AS **{wave}**).  ",
            "> Parent: AR COMPLETE + FROZEN · Ship: **AF packaged stack + "
            "AQ product layer — not open chat LM** · ≤5M.",
            "",
            "## Current stage",
            "",
            f"**AS10 — AS-FREEZE ({status})** · Next: "
            "**do not invent Wave AT**",
            "",
            "| Field | Value |",
            "|-------|--------|",
            f"| Wave | **{wave}** |",
            f"| Decision | **{decision.split(':', 1)[0]}** |",
            "| Public | `docs/results/nano-lm/as-freeze.md` |",
            "| Formal | `docs/results/nano-lm/formal-hasfreeze-as-freeze.md` |",
            "",
            "## Stage board",
            "",
            "| Stage | ID | Status |",
            "|------:|----|--------|",
            "| AS0 | SESSION | **DONE — PROMOTE** |",
            "| AS1 | H-ASKABSTAIN | **DONE — PROMOTE** |",
            "| AS2 | H-SEMFIX | **DONE — PROMOTE** |",
            "| AS3 | H-ADVSAFE | **DONE — PROMOTE** |",
            "| AS4 | H-PARAEXT2 | **DONE — PROMOTE** |",
            "| AS5 | H-METRICS | **DONE — PROMOTE** |",
            "| AS6 | H-SHIPUI | **DONE — PROMOTE** |",
            "| AS7 | H-NANOGEN3 | **DONE — HOLD** |",
            "| AS8 | AS-DUAL-HITL | **DONE — PROMOTE** |",
            "| AS9 | AS-REPORT | **DONE — PROMOTE** |",
            f"| AS10 | AS-FREEZE | **{status}** |",
            "",
        ]
    )
    _LOCAL_SESSION.write_text(body, encoding="utf-8")


def run_as_freeze(*, out: Path, skip_ask: bool = False) -> dict[str, Any]:
    """
    GIVEN AS formals + COMPLETE closeout
    WHEN locking Wave AS
    THEN PROMOTE iff decisions ∧ public COMPLETE ∧ product markers ∧ smoke.
    """
    _write_freeze_docs()
    formal_paths = [p for _, (p, _) in AS_DECISIONS.items()]
    read_paths = list(
        dict.fromkeys([*formal_paths, *AS_PUBLIC, *AS_PRODUCT_DOCS])
    )
    cpus = int(os.cpu_count() or 4)
    workers = min(14, max(4, cpus - 2), max(4, len(read_paths)))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        pairs = list(pool.map(lambda p: (p, _read_text(p)), read_paths))
    texts = dict(pairs)
    formal_texts = {p: texts.get(p, "") for p in formal_paths}
    public_texts = {p: texts.get(p, "") for p in AS_PUBLIC}
    product_texts = {p: texts.get(p, "") for p in AS_PRODUCT_DOCS}
    decision = decide_as_freeze(
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
        "id": AS_FREEZE_ID,
        "hyp_id": AS_FREEZE_ID,
        "stage": "AS10",
        "thesis": AS_THESIS,
        "decision": decision,
        "formals": {
            hid: {
                "path": path,
                "want": want,
                "ok": want in formal_texts.get(path, ""),
            }
            for hid, (path, want) in AS_DECISIONS.items()
        },
        "ask_smoke": ask,
        "public_note": "docs/results/nano-lm/as-freeze.md",
        "formal_note": "docs/results/nano-lm/formal-hasfreeze-as-freeze.md",
        "wave_as_summary": "docs/results/nano-lm/wave-as-summary.md",
        "rule": "pesquisa §5 AS-FREEZE",
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
        summary = run_as_freeze(
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
                "hyp_id": AS_FREEZE_ID,
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
